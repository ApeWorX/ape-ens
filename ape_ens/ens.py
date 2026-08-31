from functools import cached_property
from typing import TYPE_CHECKING, Optional

from ape.exceptions import NetworkError, NetworkNotFoundError, ProviderError
from ape.logging import logger
from ape.utils.basemodel import ManagerAccessMixin
from ens.exceptions import ResolverNotFound  # type: ignore[import-untyped]
from web3.exceptions import BadFunctionCallOutput, CannotHandleRequest, Web3RPCError
from web3.main import ENS as Web3ENS

from ape_ens.exceptions import (
    AmbiguousNetworkError,
    ApeENSException,
    ConflictingResolveOptionsError,
    LocalNetworkCoinTypeError,
    MissingRegistryError,
    UnknownNetworkError,
)
from ape_ens.utils.coin_type import DEFAULT_EVM_COIN_TYPE, ETH_COIN_TYPE, coin_type_from_chain_id
from ape_ens.utils.namehash import namehash

if TYPE_CHECKING:
    from ape.api.networks import EcosystemAPI, NetworkAPI
    from ape.types import AddressType
    from ape_ethereum.provider import Web3Provider
    from hexbytes import HexBytes

    from ape_ens.config import ENSConfig


# TODO: Use `ape.logging.silenced` in 0.8.26.
def silenced(func):
    def wrapper(*args, **kwargs):
        level = logger.level
        logger.set_level(100_000)
        try:
            return func(*args, **kwargs)
        finally:
            logger.set_level(level)

    return wrapper


class ENS(ManagerAccessMixin):
    """
    An Ape wrapper around ENS functionality. Handles mainnet
    network connections when necessary.

    Forward resolution (``resolve()``) and text records (``get_text()``)
    use web3.py's ENS client. With web3.py >= 7.16.0, those reads go
    through the ENS Universal Resolver (ENSv2-ready). ``owner()`` still
    queries the ENS registry directly.
    """

    def __init__(self, backend: Optional["Web3ENS"] = None) -> None:
        self.__initialized_ens = backend
        self.local_registry: dict[str, AddressType] = {}

    @classmethod
    def is_valid_name(cls, name: str) -> bool:
        """
        Returns True if the name is valid. No network connection
        is required to check the validity of a name.

        Args:
            name (str): The name to check.

        Returns:
            bool
        """
        return Web3ENS.is_valid_name(name)

    @cached_property
    def _mainnet_provider(self) -> "Web3Provider":
        """
        An Ethereum mainnet connect is required to use ENS.
        Use this helper method across the ape-ens plugin to obtain
        the connected Ethereum provider for interacting with ENS.
        """
        return self._get_mainnet_provider()

    @silenced
    def _get_mainnet_provider(self) -> "Web3Provider":
        provider = self.network_manager.active_provider
        if (
            provider
            and hasattr(provider, "web3")
            and provider.network.name in ("mainnet", "mainnet-fork")
            and provider.network.ecosystem.name == "ethereum"
        ):
            return provider

        ethereum = self.network_manager.ethereum

        # Find a provider with access to web3.ens.
        # First, try the default ethereum mainnet provider.
        web3_provider = None
        if provider := ethereum.mainnet.default_provider:
            if "web3" in dir(provider):
                web3_provider = provider

        if web3_provider is None:
            # Loop through other providers to find a valid one.
            # It should minimally find ape-node which comes with Ape.
            for provider in ethereum.mainnet.providers:
                if "web3" in dir(provider):
                    web3_provider = provider
                    break

        if web3_provider is None:
            raise ValueError("Never found a valid Ethereum mainnet provider.")

        # Connect the provider so we can access web3.ens.
        if not web3_provider.is_connected:
            try:
                web3_provider.connect()

            except ProviderError:
                # There might be an issue, but attempt anyway.
                return web3_provider

            except KeyError:
                # Once https://github.com/ApeWorX/ape/pull/2496 is released,
                # (Ape 0.8.26) we can remove this except block.
                return web3_provider

        return web3_provider

    @cached_property
    def _web3_ens(self) -> "Web3ENS":
        if ens := self.__initialized_ens:
            # Initialized with ENS (testing?)
            return ens

        return self._create_web3_ens()

    @property
    def config(self) -> "ENSConfig":
        return self.config_manager.ens

    def _create_web3_ens(self, registry_address: Optional["AddressType"] = None) -> "Web3ENS":
        if registry_address:
            return Web3ENS.from_web3(self._mainnet_provider.web3, registry_address)

        else:
            # Check config.
            if address := self.config.registry_address:
                return Web3ENS.from_web3(self._mainnet_provider.web3, address)

        # Use default (most common).
        return self._mainnet_provider.web3.ens

    def _get_backend(self, registry_address: Optional["AddressType"] = None) -> "Web3ENS":
        if registry_address:
            return self._create_web3_ens(registry_address=registry_address)

        return self._web3_ens

    @staticmethod
    def _cache_key(name: str, coin_type: Optional[int] = None) -> str:
        # ENSIP-9: 60 is ETH, the same as omitting coin_type.
        if coin_type in (None, 60):
            return name
        return f"{name}:{coin_type}"

    def can_resolve(self, name: str) -> bool:
        """
        Returns ``True`` when ENS can resolve the name.

        Args:
            name (str): The name to check.

        Returns:
            bool
        """
        if "." not in name or not self.is_valid_name(name):
            return False

        try:
            address = self.resolve(name)
        except CannotHandleRequest:
            # Either this is not actually mainnet or our head is
            # pointed before ENS existed.
            return False

        return address is not None

    def resolve(
        self,
        name: str,
        use_cache: Optional[bool] = None,
        registry_address: Optional["AddressType"] = None,
        coin_type: Optional[int] = None,
        ecosystem: Optional[str] = None,
        network: Optional[str] = None,
    ) -> Optional["AddressType"]:
        """
        Resolve an ENS name.

        With web3.py >= 7.16.0, this uses the ENS Universal Resolver.
        Pass ``coin_type`` for ENSIP-9/11 multichain records (for example
        ``0x80000000 | chain_id`` on EVM L2s). Ethereum L1 (mainnet and
        testnets) uses coin type 60.

        When ``coin_type`` / ``ecosystem`` / ``network`` are omitted, coin type
        follows the connected Ape network. L2s query that chain's record, then
        the ENSIP-19 default EVM record (``0x80000000``), not the Ethereum
        (60) record. Local sessions and disconnected use stay coin type 60.
        ``ape.convert`` uses the same path. ENS RPC is still Ethereum mainnet.

        Alternatively, pass Ape ``ecosystem`` / ``network`` names (for example
        ``ecosystem="base", network="mainnet"``) to select the coin type
        explicitly. These do not change which RPC is used for ENS.

        Args:
            name (str): The name to resolve.
            use_cache (bool): Set to ``False`` to not use the in-memory cache.
            registry_address (Optional[AddressType]): Optionally, change the registry
              address.
            coin_type (Optional[int]): Optionally, resolve a non-ETH coin type.
            ecosystem (Optional[str]): Ape ecosystem name for ENSIP-11 coin type.
            network (Optional[str]): Ape network name for ENSIP-11 coin type.
              May be ``"base"`` when that uniquely names an ecosystem,
              ``"base:mainnet"``, or ``"base:mainnet:node"`` (provider is ignored).

        Returns:
            AddressType | None
        """
        if coin_type is not None and (ecosystem is not None or network is not None):
            raise ConflictingResolveOptionsError(
                "Cannot pass coin_type together with ecosystem or network. "
                "Use coin_type for a raw ENSIP-9/11 value, or ecosystem/network "
                "for Ape chain names."
            )

        if ecosystem is not None or network is not None:
            coin_type = self._coin_type_from_ape_network(ecosystem, network)
        elif coin_type is None:
            coin_type = self._coin_type_from_connected_network()

        # ENSIP-9: coin type 60 is ETH, same as the default addr() path.
        if coin_type == 60:
            coin_type = None

        ens = self._get_backend(registry_address)
        if use_cache is None:
            # Use default from config.
            use_cache = self.config.use_cache

        cache_key = self._cache_key(name, coin_type)
        if use_cache:
            if address := self.local_registry.get(cache_key):
                return address

            # Config registry is ETH-address mappings only.
            if coin_type is None:
                if address := self.config.registry.get(name):
                    self.local_registry[cache_key] = address
                    return address

        try:
            address = (
                ens.address(name, coin_type=coin_type)
                if coin_type is not None
                else ens.address(name)
            )
            # ENSIP-19: chain-specific miss → default EVM, never ETH (60).
            if address is None and coin_type is not None and coin_type != DEFAULT_EVM_COIN_TYPE:
                address = ens.address(name, coin_type=DEFAULT_EVM_COIN_TYPE)
        except (Web3RPCError, BadFunctionCallOutput) as err:
            raise MissingRegistryError(str(err))

        if use_cache and address is not None:
            self.local_registry[cache_key] = address

        return address

    def _coin_type_from_connected_network(self) -> Optional[int]:
        provider = self.network_manager.active_provider
        if provider is None:
            return None

        net = provider.network
        if net.is_local:
            return None

        try:
            return self._coin_type_from_ape_network(net.ecosystem.name, net.name)
        except ApeENSException:
            return None

    def _coin_type_from_ape_network(
        self,
        ecosystem: Optional[str] = None,
        network: Optional[str] = None,
    ) -> int:
        eco_name, net_name = self._parse_ape_network(ecosystem, network)
        eco = self._ape_ecosystem(eco_name)
        net = self._ape_network(eco, net_name)
        if net.is_local:
            raise LocalNetworkCoinTypeError(
                "Cannot derive an ENS coin type from Ape local networks. "
                "Pass coin_type=60 (ETH) or a live ecosystem and network "
                "such as ecosystem='ethereum', network='mainnet'."
            )

        # ENSIP-19: L1 testnets (Sepolia, Holesky, …) share coin type 60.
        if eco.name == "ethereum":
            return ETH_COIN_TYPE

        return coin_type_from_chain_id(self._chain_id_for_ens(net))

    def _ape_ecosystem(self, name: str) -> "EcosystemAPI":
        try:
            return self.network_manager.get_ecosystem(name)
        except NetworkError as err:
            raise UnknownNetworkError(str(err)) from err

    def _ape_network(self, ecosystem: "EcosystemAPI", name: str) -> "NetworkAPI":
        try:
            return ecosystem.get_network(name)
        except NetworkError as err:
            raise UnknownNetworkError(str(err)) from err

    def _parse_ape_network(
        self,
        ecosystem: Optional[str],
        network: Optional[str],
    ) -> tuple[str, str]:
        if ecosystem is not None:
            eco = self._ape_ecosystem(ecosystem)
            if network is None:
                return eco.name, self._default_ens_network_name(eco)
            return eco.name, network

        assert network is not None
        if choice := self._parse_network_choice(network):
            return choice

        matched_eco: Optional["EcosystemAPI"] = None
        try:
            matched_eco = self.network_manager.get_ecosystem(network)
        except NetworkError:
            pass

        if matched_eco is not None:
            return matched_eco.name, self._default_ens_network_name(matched_eco)

        matches = self._match_network_name(network)
        if len(matches) == 1:
            return matches[0]

        if len(matches) > 1:
            options = ", ".join(f"{eco}:{net}" for eco, net in matches)
            raise AmbiguousNetworkError(
                f"network={network!r} is ambiguous ({options}). Pass ecosystem= as well."
            )

        raise UnknownNetworkError(f"Unknown Ape ecosystem or network {network!r}.")

    @staticmethod
    def _parse_network_choice(network: str) -> Optional[tuple[str, str]]:
        """Split ``ecosystem:network`` or ``ecosystem:network:provider``.

        The provider segment is ignored; coin type does not use an RPC.
        """
        if ":" not in network:
            return None

        parts = network.split(":")
        if len(parts) >= 2 and parts[0] and parts[1]:
            return parts[0], parts[1]
        return None

    def _default_ens_network_name(self, ecosystem: "EcosystemAPI") -> str:
        if "mainnet" in ecosystem.networks:
            return "mainnet"

        default = ecosystem.default_network_name
        if default != "local":
            return default

        raise AmbiguousNetworkError(f"Specify network= for ecosystem '{ecosystem.name}'.")

    def _match_network_name(self, network_name: str) -> list[tuple[str, str]]:
        matches: list[tuple[str, str]] = []
        seen: set[tuple[str, str]] = set()

        for eco in self.network_manager.ecosystems.values():
            try:
                net = eco.get_network(network_name)
            except NetworkNotFoundError:
                continue

            key = (eco.name, net.name)
            if key not in seen:
                seen.add(key)
                matches.append(key)

        return matches

    def _chain_id_for_ens(self, network: "NetworkAPI") -> int:
        try:
            if network.is_fork:
                return int(network.upstream_chain_id)  # type: ignore[attr-defined]
            return network.chain_id
        except (AttributeError, NetworkError, TypeError) as err:
            raise ApeENSException(
                f"Unable to determine chain ID for '{network.ecosystem.name}:{network.name}'."
            ) from err

    def name(
        self, address: "AddressType", registry_address: Optional["AddressType"] = None
    ) -> Optional[str]:
        """
        Reverse look-up an address to get the ENS name.

        Args:
            address (AddressType): The address to resolve.
            registry_address (Optional[AddressType]): Optionally, change the registry.

        Returns:
            str | None: The ENS name.
        """
        return self._get_backend(registry_address).name(address)

    def owner(
        self, name: str, registry_address: Optional["AddressType"] = None
    ) -> Optional["AddressType"]:
        """
        Get the ENS registry owner of a domain.

        This is ``registry.owner(node)``, not the Universal Resolver path
        used by ``resolve()``. Wrapped names typically show the Name Wrapper.

        Args:
            name (str): The ENS name to check.
            registry_address (Optional[AddressType]): Optionally, change the registry.

        Returns:
            AddressType | None
        """
        return self._get_backend(registry_address).owner(name)

    def get_text(
        self,
        name: str,
        key: str,
        registry_address: Optional["AddressType"] = None,
    ) -> Optional[str]:
        """
        Get a text record for an ENS name.

        Uses the same Universal Resolver read path as ``resolve()``
        (web3.py >= 7.16.0).

        Args:
            name (str): The ENS name.
            key (str): The text record key (e.g. ``"description"``, ``"url"``,
              ``"com.github"``).
            registry_address (Optional[AddressType]): Optionally, change the registry.

        Returns:
            str | None: The record value, or ``None`` if unset.
        """
        try:
            value = self._get_backend(registry_address).get_text(name, key)
        except (Web3RPCError, BadFunctionCallOutput) as err:
            raise MissingRegistryError(str(err))
        except ResolverNotFound:
            return None

        return value or None

    def namehash(self, name: str) -> "HexBytes":
        """
        Get the namehash of an ENS name.

        Args:
            name (str): The ENS name to check.

        Returns:
            HexBytes
        """
        return namehash(name)

from functools import cached_property
from typing import TYPE_CHECKING, Optional

from ape.exceptions import ProviderError
from ape.logging import logger
from ape.utils.basemodel import ManagerAccessMixin
from web3.exceptions import BadFunctionCallOutput, CannotHandleRequest, Web3RPCError
from web3.main import ENS as Web3ENS

from ape_ens.exceptions import MissingRegistryError
from ape_ens.utils.namehash import namehash

if TYPE_CHECKING:
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
    ) -> Optional["AddressType"]:
        """
        Resolve an ENS name.

        Args:
            name (str): The name to resolve.
            use_cache (bool): Set to ``False`` to not use the in-memory cache.
            registry_address (Optional[AddressType]): Optionally, change the registry
              address.

        Returns:
            AddressType | None
        """
        ens = (
            self._create_web3_ens(registry_address=registry_address)
            if registry_address
            else self._web3_ens
        )
        if use_cache is None:
            # Use default from config.
            use_cache = self.config.use_cache

        if use_cache:
            if address := self.local_registry.get(name):
                return address

            # Check config cache.
            if address := self.config.registry.get(name):
                self.local_registry[name] = address
                return address

        try:
            address = ens.address(name)
        except (Web3RPCError, BadFunctionCallOutput) as err:
            raise MissingRegistryError(str(err))

        if use_cache and address is not None:
            self.local_registry[name] = address

        return address

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
        ens = (
            self._create_web3_ens(registry_address=registry_address)
            if registry_address
            else self._web3_ens
        )
        return ens.name(address)

    def owner(
        self, name: str, registry_address: Optional["AddressType"] = None
    ) -> Optional["AddressType"]:
        """
        Get the owner of an ENS domain.

        Args:
            name (str): The ENS name to check.
            registry_address (Optional[AddressType]): Optionally, change the registry.

        Returns:
            AddressType | None
        """
        ens = (
            self._create_web3_ens(registry_address=registry_address)
            if registry_address
            else self._web3_ens
        )
        return ens.owner(name)

    def namehash(self, name: str) -> "HexBytes":
        """
        Get the namehash of an ENS name.

        Args:
            name (str): The ENS name to check.

        Returns:
            HexBytes
        """
        return namehash(name)

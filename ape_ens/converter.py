from typing import Any, Optional

from ape.api import ConverterAPI
from ape.exceptions import NetworkError, ProviderError
from ape.logging import logger
from ape.types import AddressType
from ape.utils import cached_property
from ape_ethereum.provider import Web3Provider
from web3.exceptions import CannotHandleRequest
from web3.main import ENS


class ENSConversions(ConverterAPI):
    """Converts ENS names like `my-name.eth` to `0xAbCd...1234`"""

    address_cache: dict[str, AddressType] = {}

    @cached_property
    def mainnet_provider(self) -> Optional[Web3Provider]:
        provider = self.network_manager.active_provider
        if (
            provider
            and isinstance(provider, Web3Provider)
            and provider.network.name in ("mainnet", "mainnet-fork")
            and provider.network.ecosystem.name == "ethereum"
        ):
            return provider

        # Connect to mainnet for ENS resolution
        # NOTE: May not work unless the user configures their default mainnet provider.
        ecosystem = self.network_manager.get_ecosystem("ethereum")
        mainnet = ecosystem.get_network("mainnet")
        if not (provider := mainnet.default_provider):
            return None

        elif not isinstance(provider, Web3Provider):
            logger.warning(
                "Unable to connect to mainnet provider to "
                "perform ENS lookup (must be a Web3Provider)"
            )
            return None

        if not provider.is_connected:
            # Connect if needed.
            try:
                provider.connect()
            except ProviderError:
                logger.warning(
                    "Unable to connect to mainnet provider to perform ENS lookup. "
                    "Try changing your default mainnet provider."
                )
                return None

        return provider

    def is_convertible(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        elif "." not in value:
            return False

        elif not ENS.is_valid_name(value):
            return False

        elif value in self.address_cache:
            return True

        else:
            try:
                provider = self.mainnet_provider
                if not provider:
                    return False

                elif not (ens := provider.web3.ens):
                    return False

                try:
                    address = ens.address(value)
                except CannotHandleRequest:
                    # Either this is not actually mainnet or our head is
                    # pointed before ENS existed.
                    return False

                if address is not None:
                    self.address_cache[value] = address
                    return True

                return False

            except (NetworkError, ProviderError):
                return False

    def convert(self, value: str) -> AddressType:
        if value in self.address_cache:
            return self.address_cache[value]

        elif not (provider := self.mainnet_provider):
            # Should never get here.
            raise ValueError(f"Unable to convert ENS value '{value}'.")

        # TODO: Switch to using ENS SDK
        if not (ens := provider.web3.ens):
            # Should never get here.
            raise ValueError(f"Unable to convert ENS value '{value}'.")

        address = ens.address(value)
        self.address_cache[value] = address
        return address

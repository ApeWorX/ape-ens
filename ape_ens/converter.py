from typing import Any, Dict, Optional

from ape.api import ConverterAPI, Web3Provider
from ape.exceptions import NetworkError, ProviderError
from ape.logging import logger
from ape.types import AddressType
from ape.utils import cached_property
from web3.main import ENS


class ENSConversions(ConverterAPI):
    """Converts ENS names like `my-name.eth` to `0xAbCd...1234`"""

    address_cache: Dict[str, AddressType] = {}

    @cached_property
    def mainnet_provider(self) -> Optional[Web3Provider]:
        provider = self.network_manager.active_provider
        if provider and isinstance(provider, Web3Provider) and provider.network.name == "mainnet":
            return provider

        # Connect to mainnet for ENS resolution
        # NOTE: May not work unless the user configures their default mainnet provider.
        provider = self.network_manager.get_provider_from_choice("ethereum:mainnet")
        if not isinstance(provider, Web3Provider):
            logger.warning(
                "Unable to connect to mainnet provider to "
                "perform ENS lookup (must be a Web3Provider)"
            )
            return None

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

                ens = provider.web3.ens
                if not ens:
                    return False

                address = ens.address(value)

                if address is not None:
                    self.address_cache[value] = address
                    return True

                return False
            except (NetworkError, ProviderError):
                return False

    def convert(self, value: str) -> AddressType:
        if value in self.address_cache:
            return self.address_cache[value]

        provider = self.mainnet_provider
        if not provider:
            # Should never get here.
            raise ValueError(f"Unable to convert ENS value '{value}'.")

        # TODO: Switch to using ENS SDK
        ens = provider.web3.ens
        if not ens:
            # Should never get here.
            raise ValueError(f"Unable to convert ENS value '{value}'.")

        address = ens.address(value)
        self.address_cache[value] = address
        return address

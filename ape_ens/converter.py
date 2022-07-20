from typing import Any, Dict

from ape.api import ConverterAPI, Web3Provider
from ape.exceptions import NetworkError, ProviderError
from ape.types import AddressType
from web3.main import ENS
from ape.utils import cached_property


class ENSConversions(ConverterAPI):
    """Converts ENS names like `my-name.eth` to `0xAbCd...1234`"""

    address_cache: Dict[str, AddressType] = {}

    @cached_property
    def mainnet_provider(self) -> Web3Provider:
        provider = self.network_manager.active_provider
        if (
            not provider
            or not isinstance(provider, Web3Provider)
            or not provider.network.name == "mainnet"
        ):
            provider = self.network_manager.get_provider_from_choice("ethereum:mainnet")
            provider.connect()

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
                address = self.mainnet_provider.web3.ens.address(value)

                if address is not None:
                    self.address_cache[value] = address
                    return True

                return False
            except (NetworkError, ProviderError):
                return False

    def convert(self, value: str) -> AddressType:
        if value in self.address_cache:
            return self.address_cache[value]

        address = self.mainnet_provider.web3.ens.address(value)
        self.address_cache[value] = address
        return address

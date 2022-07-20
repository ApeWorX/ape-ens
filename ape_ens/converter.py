from contextlib import contextmanager
from typing import Any, Dict

from ape.api import ConverterAPI, Web3Provider
from ape.exceptions import NetworkError, ProviderError
from ape.types import AddressType
from web3.main import ENS


class ENSConversions(ConverterAPI):
    """Converts ENS names like `my-name.eth` to `0xAbCd...1234`"""

    resolver_cache: Dict[str, AddressType] = {}

    def is_convertible(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        elif "." not in value:
            return False

        elif not ENS.is_valid_name(value):
            return False

        elif value in self.resolver_cache:
            return True

        else:
            try:
                with self._connect_to_ens() as ens:
                    return ens.address(value) is not None
            except (NetworkError, ProviderError):
                return False

    def convert(self, value: str) -> AddressType:
        if value in self.resolver_cache:
            return self.resolver_cache[value]

        with self._connect_to_ens() as ens:
            address = ens.address(value)
            self.resolver_cache[value] = address
            return address

    @contextmanager
    def _connect_to_ens(self):
        def _get_ens_from_provider(provider_):
            if not isinstance(provider_, Web3Provider):
                raise NotImplementedError("Currently, only web3 providers work with this plugin.")

            web3 = provider_._web3

            if not hasattr(web3, "ens"):
                raise NotImplementedError("This provider does not implement ENS calls.")

            return web3.ens

        provider = self.network_manager.active_provider
        if provider and provider.network.name == "mainnet":
            yield _get_ens_from_provider(provider)

        else:
            with self.network_manager.parse_network_choice("ethereum:mainnet") as provider:
                yield _get_ens_from_provider(provider)
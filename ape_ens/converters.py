from typing import Any, Optional

from ape.api import ConverterAPI, Web3Provider
from ape.exceptions import ProviderError
from ape.logging import logger
from ape.types import AddressType
from ape.utils import cached_property
from web3.main import ENS


class ENSConversions(ConverterAPI):
    """Converts ENS names like `my-name.eth` to `0xAbCd...1234`"""

    @cached_property
    def ens(self) -> Optional[ENS]:
        provider = self.networks.active_provider

        if not provider:
            raise ProviderError("Not connected to a provider.")

        if not isinstance(provider, Web3Provider):
            raise NotImplementedError("Currently, only web3 providers work with this plugin.")

        web3 = provider._web3

        if not hasattr(web3, "ens"):
            raise NotImplementedError("This provider does not implement ENS calls.")

        return web3.ens

    def is_convertible(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        elif not ENS.is_valid_name(value):
            return False

        elif not self.ens:
            logger.warning("Ethereum Mainnet provider not available for ENS address lookups")
            return False

        else:
            return self.ens.address(value) is not None

    def convert(self, value: str) -> AddressType:
        assert self.ens  # NOTE: Just to make mypy happy
        return self.ens.address(value)

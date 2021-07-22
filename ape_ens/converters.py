import os
from typing import Any, Optional

from ape.api import ConverterAPI
from ape.types import AddressType
from ape.utils import cached_property, notify
from ens import ENS  # type: ignore
from web3 import HTTPProvider, Web3  # type: ignore


class ENSConversions(ConverterAPI):
    """Converts ENS names like `my-name.eth` to `0xAbCd...1234`"""

    @cached_property
    def ens(self) -> Optional[ENS]:
        key = os.environ.get("WEB3_INFURA_PROJECT_ID") or os.environ.get("WEB3_INFURA_API_KEY")

        if key:  # Infura key
            web3 = Web3(HTTPProvider(f"https://mainnet.infura.io/v3/{key}"))
            return web3.ens

        # TODO: Add other provider types
        # TODO: See if we can use `self.networks` somehow instead to connect to Ethereum mainnet

        return None

    def is_convertible(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        elif not ENS.is_valid_name(value):
            return False

        elif not self.ens:
            notify("WARNING", "Ethereum Mainnet provider not available for ENS address lookups")
            return False

        else:
            return self.ens.address(value) is not None

    def convert(self, value: str) -> AddressType:
        assert self.ens  # NOTE: Just to make mypy happy
        return self.ens.address(value)

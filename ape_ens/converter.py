from typing import Any

from ape.api import ConverterAPI
from ape.types import AddressType
from web3.exceptions import CannotHandleRequest

from ape_ens.ens import ENS


class ENSConversions(ConverterAPI):
    """Converts ENS names like `my-name.eth` to `0xAbCd...1234`"""

    address_cache: dict[str, AddressType] = {}

    def __init__(self, *args, **kwargs) -> None:
        ens = kwargs.pop("ens", None)
        super().__init__(*args, **kwargs)
        self._ens = ens

    @property
    def ens(self) -> ENS:
        """
        Ape's wrapper around ENS functionality.
        """
        if ens := self._ens:
            return ens

        ens = ENS()  # Default behavior.
        self._ens = ens
        return ens

    def is_convertible(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        elif "." not in value:
            return False

        elif not ENS.is_valid_name(value):
            return False

        elif value in self.address_cache:
            return True

        elif not (ens := self.ens):
            return False

        try:
            address = ens.resolve(value)
        except CannotHandleRequest:
            # Either this is not actually mainnet or our head is
            # pointed before ENS existed.
            return False

        if address is None:
            return False

        self.address_cache[value] = address
        return True

    def convert(self, value: str) -> AddressType:
        if value in self.address_cache:
            # It will also be cached if `.is_convertible()` called.
            return self.address_cache[value]

        elif not (ens := self.ens):
            raise ValueError(f"Unable to convert ENS value '{value}'.")

        address = ens.resolve(value)
        self.address_cache[value] = address
        return address

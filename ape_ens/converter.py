from typing import TYPE_CHECKING, Any

from ape.api import ConverterAPI

from ape_ens.ens import ENS

if TYPE_CHECKING:
    from ape.types import AddressType


class ENSConversions(ConverterAPI):
    """Converts ENS names like `my-name.eth` to `0xAbCd...1234`"""

    def __init__(self, *args, **kwargs) -> None:
        ens = kwargs.pop("ens", None)
        super().__init__(*args, **kwargs)
        self._ens: ENS = ens

    @property
    def address_cache(self) -> dict[str, "AddressType"]:
        return self.ens.local_registry

    @address_cache.setter
    def address_cache(self, value: dict[str, "AddressType"]) -> None:
        self.ens.local_registry = value

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

        return self.ens.can_resolve(value)

    def convert(self, value: str) -> "AddressType":
        return self.ens.resolve(value)

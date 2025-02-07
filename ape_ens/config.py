from typing import Optional

from ape.api import PluginConfig
from ape.types import AddressType


class ENSConfig(PluginConfig):
    """
    Configure the ENS plugin.
    """

    use_cache: bool = True
    """
    Set to ``False`` to never cache ENS name resolutions and
    always fetch from Ethereum.
    """

    registry: dict[str, str] = {}
    """
    Hardcode entries in the registry to avoid connecting
    to Ethereum mainnet to resolve. This is useful for
    performance and in testing environments without access
    to Ethereum mainnet.
    """

    registry_address: Optional[AddressType] = None
    """
    Configure the registry address if it different than the default
    Ethereum mainnet address.
    """

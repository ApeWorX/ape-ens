from ape import plugins
from ape.types import AddressType

from .converters import ENSConversions


@plugins.register(plugins.ConversionPlugin)
def converters():
    yield AddressType, ENSConversions

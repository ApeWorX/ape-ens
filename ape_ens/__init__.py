from ape import plugins
from ape.types import AddressType

from .converters import ENSConfig, ENSConversions


@plugins.register(plugins.Config)
def config_class():
    return ENSConfig


@plugins.register(plugins.ConversionPlugin)
def converters():
    yield AddressType, ENSConversions

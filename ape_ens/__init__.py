from ape import plugins


@plugins.register(plugins.ConversionPlugin)
def converters():
    from ape.types import AddressType

    from ape_ens.converter import ENSConversions

    yield AddressType, ENSConversions


@plugins.register(plugins.Config)
def config_class():
    from ape_ens.config import ENSConfig

    return ENSConfig


def __getattr__(name: str):
    if name == "ENS":
        from ape_ens.ens import ENS

        return ENS

    elif name == "ENSConfig":
        from ape_ens.config import ENSConfig

        return ENSConfig

    elif name == "ENSConversions":
        from ape_ens.converter import ENSConversions

        return ENSConversions

    raise AttributeError(name)


__all__ = ["ENS", "ENSConfig", "ENSConversions"]

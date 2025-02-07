from ape import plugins


@plugins.register(plugins.ConversionPlugin)
def converters():
    from ape.types import AddressType

    from ape_ens.converter import ENSConversions

    yield AddressType, ENSConversions


def __getattr__(name: str):
    if name == "ENS":
        from ape_ens.ens import ENS

        return ENS

    elif name == "ENSConversions":
        from ape_ens.converter import ENSConversions

        return ENSConversions

    raise AttributeError(name)


__all__ = ["ENS", "ENSConversions"]

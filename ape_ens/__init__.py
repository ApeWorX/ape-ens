from ape import plugins


@plugins.register(plugins.ConversionPlugin)
def converters():
    from ape.types import AddressType

    from ape_ens.converter import ENSConversions

    yield AddressType, ENSConversions


def __getattr__(name: str):
    if name == "ENSConversions":
        from ape_ens.converter import ENSConversions

        return ENSConversions

    raise AttributeError(name)


__all__ = ["ENSConversions"]

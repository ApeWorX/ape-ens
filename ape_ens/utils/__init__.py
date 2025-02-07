def __getattr__(name: str):
    if name == "namehash":
        from .namehash import namehash

        return namehash

    raise AttributeError(name)


__all__ = ["namehash"]

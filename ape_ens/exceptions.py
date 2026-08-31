from ape.exceptions import ApeException


class ApeENSException(ApeException):
    """
    Base class for exceptions in the `ape-ens` package.
    """


class MissingRegistryError(ApeENSException):
    """
    Raised when ape-ens detect the registry is missing.
    """


class ConflictingResolveOptionsError(ApeENSException):
    """
    Raised when ``coin_type`` is combined with ``ecosystem`` or ``network``.
    """


class AmbiguousNetworkError(ApeENSException):
    """
    Raised when an Ape network name is not unique across ecosystems.
    """


class UnknownNetworkError(ApeENSException):
    """
    Raised when an Ape ecosystem or network name cannot be resolved.
    """


class LocalNetworkCoinTypeError(ApeENSException):
    """
    Raised when mapping Ape local networks to an ENS coin type.
    """

from ape.exceptions import ApeException


class ApeENSException(ApeException):
    """
    Base class for exceptions in the `ape-ens` package.
    """


class MissingRegistryError(ApeENSException):
    """
    Raised when ape-ens detect the registry is missing.
    """

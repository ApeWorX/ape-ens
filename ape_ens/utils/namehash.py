# from eth_utils import keccak
import codecs
import functools

from ape.exceptions import ProviderNotConnectedError
from ens.utils import raw_name_to_hash
from eth_utils import keccak
from hexbytes import HexBytes

# https://github.com/ethereum/EIPs/blob/master/EIPS/eip-137.md#namehash-algorithm


def is_bytes(value):
    return isinstance(value, (bytes, bytearray))


def combine(f, g):
    return lambda x: f(g(x))


def compose(*functions):
    return functools.reduce(combine, functions, lambda x: x)


def _sub_hash(value, label):
    return keccak(value + keccak(label))


def manual_namehash(name: str, encoding=None) -> HexBytes:
    node = b"\x00" * 32
    if name:
        if encoding is None:
            if is_bytes(name):
                encoded_name = name
            else:
                encoded_name = codecs.encode(name, "utf8")
        else:
            encoded_name = codecs.encode(name, encoding)

        labels = encoded_name.split(b".")

        return HexBytes(
            compose(*(functools.partial(_sub_hash, label=label) for label in labels))( # noqa: 501
                node
            )
        )
    return HexBytes(node)


def namehash(name: str) -> HexBytes:
    try:
        return raw_name_to_hash(name)
    except ProviderNotConnectedError:
        return manual_namehash(name)

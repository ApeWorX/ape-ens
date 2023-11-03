import codecs
import functools

from eth_utils import is_bytes, keccak
from hexbytes import HexBytes

try:
    from ens.utils import raw_name_to_hash  # type: ignore
except ImportError:
    raw_name_to_hash = None

# https://github.com/ethereum/EIPs/blob/master/EIPS/eip-137.md#namehash-algorithm


def _combine(f, g):
    return lambda x: f(g(x))


def _compose(*functions):
    return functools.reduce(_combine, functions, lambda x: x)


def _sub_hash(value, label):
    return keccak(value + keccak(label))


def _manual_namehash(name: str, encoding=None) -> HexBytes:
    node = b"\x00" * 32
    if name:
        if encoding is None:
            if is_bytes(name):
                encoded_name = name
            else:
                encoded_name = codecs.encode(name, "utf8")  # type: ignore
        else:
            encoded_name = codecs.encode(name, encoding)

        labels = encoded_name.split(b".")  # type: ignore

        return HexBytes(
            _compose(*(functools.partial(_sub_hash, label=label) for label in labels))(  # noqa: 501
                node
            )
        )
    return HexBytes(node)


def namehash(name: str) -> HexBytes:
    namehash_func = raw_name_to_hash if raw_name_to_hash else _manual_namehash
    return namehash_func(name)

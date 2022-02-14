import idna
from ape.exceptions import ConversionError
from eth_utils import keccak


class InvalidName(ConversionError):
    pass


def normalize_name(name: str) -> str:
    if not name:
        return name
    elif isinstance(name, (bytes, bytearray)):
        name = name.decode("utf-8")

    try:
        return idna.uts46_remap(name, std3_rules=True)
    except idna.IDNAError as exc:
        raise InvalidName(f"{name} is an invalid name, because {exc}") from exc


def label_to_hash(label: str) -> bytes:
    label = normalize_name(label)
    if "." in label:
        raise ValueError("Cannot generate hash for label %r with a '.'" % label)
    return keccak(text=label)


def normal_name_to_hash(name: str) -> bytes:
    node = b"\0" * 32
    if name:
        labels = name.split(".")
        for label in reversed(labels):
            labelhash = label_to_hash(label)
            assert isinstance(labelhash, bytes)
            assert isinstance(node, bytes)
            node = keccak(node + labelhash)
    return node


def get_node_id(name: str) -> bytes:
    return normal_name_to_hash(normalize_name(name))

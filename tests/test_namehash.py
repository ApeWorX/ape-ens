from eth_utils import to_hex

from ape_ens.utils.namehash import namehash


def test_namehash():
    actual = to_hex(namehash(""))
    expected = "0x0000000000000000000000000000000000000000000000000000000000000000"
    assert actual == expected

    actual = to_hex(namehash("eth"))
    expected = "0x93cdeb708b7545dc668eb9280176169d1c33cfd8ed6f04690a0bcc88a93fc4ae"
    assert actual == expected

    actual = to_hex(namehash("foo.eth"))
    expected = "0xde9b09fd7c5f901e23a3f19fecc54828e9c848539801e86591bd9801b019f84f"
    assert actual == expected

    actual = to_hex(namehash("ape.rocks.eth"))
    expected = "0x6294e43e29c5c1573554a68e6ff302fa867ab0d56b800f623c1abb77609d2b8d"
    assert actual == expected

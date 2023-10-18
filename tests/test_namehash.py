from ape_ens.utils.namehash import namehash


def test_namehash():
    assert (
        namehash("").hex()
        == "0x0000000000000000000000000000000000000000000000000000000000000000"  # noqa: 501
    )

    assert (
        namehash("eth").hex()
        == "0x93cdeb708b7545dc668eb9280176169d1c33cfd8ed6f04690a0bcc88a93fc4ae"
    )  # noqa: 501

    assert (
        namehash("foo.eth").hex()
        == "0xde9b09fd7c5f901e23a3f19fecc54828e9c848539801e86591bd9801b019f84f"
    )  # noqa: 501

    assert (
        namehash("ape.rocks.eth").hex()
        == "0x6294e43e29c5c1573554a68e6ff302fa867ab0d56b800f623c1abb77609d2b8d"
    )  # noqa: 501

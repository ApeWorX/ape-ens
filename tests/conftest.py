from contextlib import contextmanager
from typing import cast

import pytest
from ape.types import AddressType

from ape_ens.converter import ENSConversions
from ape_ens.ens import ENS

ADDRESS = cast(AddressType, "0xe2222bb6633228143C4Ce8fC4642aa33b857B332")
negative_tests = pytest.mark.parametrize(
    "value",
    (
        "test",
        ADDRESS,
        23452345,
        "0x07D75c30f0217c99BD0bbeA00806E9d5D7E8EFA33b5852694A5bAf3D8141d432",
    ),
)
REGISTRY = {"test.eth": ADDRESS, "vitalik.eth": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"}


@pytest.fixture(scope="session")
def address():
    return ADDRESS


@pytest.fixture(scope="session")
def vitalik():
    return REGISTRY["vitalik.eth"]


@pytest.fixture
def mock_web3_ens(mocker):
    web3_ens = mocker.MagicMock()

    def get_address(name):
        return REGISTRY.get(name)

    def get_name(address):
        for name, value in REGISTRY.items():
            if value == address:
                return name

    web3_ens.address.side_effect = get_address
    web3_ens.name.side_effect = get_name
    web3_ens.owner.side_effect = get_address
    return web3_ens


@pytest.fixture
def ens(mock_web3_ens):
    return ENS(backend=mock_web3_ens)


@pytest.fixture
def converter(ens):
    return ENSConversions(ens=ens)


@pytest.fixture
def trick_network(chain):
    """
    Helper to avoid having to connect to other networks,
    as CI/CD may not have plugins or setup required.
    """

    @contextmanager
    def fn(name, ecosystem=None):
        network = chain.provider.network
        initial_name = network.name
        initial_ecosystem_name = network.ecosystem.name
        network.name = name
        if ecosystem:
            network.ecosystem.name = ecosystem
        yield
        network.name = initial_name
        network.ecosystem.name = initial_ecosystem_name

    return fn

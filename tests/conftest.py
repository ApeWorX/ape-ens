import os
from functools import partial
from pathlib import Path
from typing import cast

import pytest
from ape.api import UpstreamProvider
from ape.types import AddressType
from ape_ethereum.provider import Web3Provider

from ape_ens.converter import ENSConversions

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


@pytest.fixture
def address():
    return ADDRESS


@pytest.fixture(autouse=True, scope="session")
def from_tests_dir():
    curr_dir = os.curdir
    here = Path(__file__).parent
    os.chdir(here)
    try:
        yield
    finally:
        os.chdir(curr_dir)


class MockMainnetProvider(Web3Provider, UpstreamProvider):
    name: str = "mock"
    provider_settings: dict = {}
    request_header: dict = {}

    @property
    def connection_str(self) -> str:
        return "<MOCK>"

    @property
    def is_connected(self) -> bool:
        return self._web3 is not None

    def connect(self):
        assert False, "Should be set externally"

    def disconnect(self):
        assert False, "Should be set externally"


@pytest.fixture
def provider_class(mocker):
    cls = MockMainnetProvider

    def connect(provider):
        provider._web3 = mocker.MagicMock()

    def disconnect(provider):
        provider._web3 = None

    cls.connect = connect
    cls.disconnect = disconnect

    return cls


@pytest.fixture
def converter(address, provider_class):
    ens = ENSConversions()

    def delete_caches():
        if "mainnet_provider" in ens.__dict__:
            del ens.__dict__["mainnet_provider"]
        if address in ens.address_cache:
            del ens.address_cache[address]

    delete_caches()

    mainnet = ens.network_manager.ethereum.mainnet
    mainnet_fork = ens.network_manager.ethereum.get_network("mainnet-fork")
    polygon_mainnet = ens.network_manager.polygon.mainnet

    mainnet_provider = partial(provider_class, name="mock-mainnet", network=mainnet)
    mainnet_fork_provider = partial(provider_class, name="mock-mainnet-fork", network=mainnet_fork)
    polygon_mainnet_provider = partial(
        provider_class, name="mock-polygon-mainnet", network=polygon_mainnet
    )

    mainnet.providers["mock-mainnet"] = mainnet_provider
    mainnet_fork.providers["mock-mainnet-fork"] = mainnet_fork_provider
    polygon_mainnet.providers["mock-polygon-mainnet"] = polygon_mainnet_provider

    mainnet.set_default_provider("mock-mainnet")
    mainnet_fork.set_default_provider("mock-mainnet-fork")
    polygon_mainnet.set_default_provider("mock-polygon-mainnet")

    yield ens

    delete_caches()


@pytest.fixture
def mainnet_provider(converter):
    _ = converter.is_convertible("test.eth")  # Set mainnet_provider
    return converter.__dict__["mainnet_provider"]

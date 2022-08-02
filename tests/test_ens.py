from functools import partial
from pathlib import Path

import pytest
from ape.api import Web3Provider
from ape.types import AddressType

from ape_ens.converter import ENSConversions


@pytest.fixture
def provider_class(mocker):
    class MockMainnetProvider(Web3Provider):
        name = "mock"
        provider_settings = {}
        data_folder = Path(".")
        request_header = {}

        def connect(self):
            self._web3 = mocker.MagicMock()

        def disconnect(self):
            self._web3 = None  # type: ignore

    return MockMainnetProvider


@pytest.fixture
def converter(provider_class):
    ens = ENSConversions()
    mainnet = ens.network_manager.ethereum.mainnet
    provider = partial(provider_class, network=mainnet)
    mainnet.providers["mock"] = provider
    mainnet.set_default_provider("mock")
    return ens


def test_is_convertible(converter):
    assert converter.is_convertible("test.eth")


@pytest.mark.parametrize(
    "value",
    (
        "test",
        "0xe1122aa5533228143C4Ce8fC4642aa33b857B332",
        23452345,
        "0x07D75c30f0217c99BD0bbeA00806E9d5D7E8EFA33b5852694A5bAf3D8141d432",
    ),
)
def test_is_not_convertible(converter, value):
    assert not converter.is_convertible(value)


def test_address_cache(converter):
    new_address: AddressType = "0xe2222bb6633228143C4Ce8fC4642aa33b857B332"  # type: ignore
    converter.address_cache["test.eth"] = new_address
    assert converter.convert("test.eth") == new_address

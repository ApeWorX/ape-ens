from functools import partial
from pathlib import Path

import pytest
from ape.api import Web3Provider

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


def test_is_not_convertible(converter):
    assert not converter.is_convertible("test")
    assert not converter.is_convertible("0xe1122aa5533228143C4Ce8fC4642aa33b857B332")
    assert not converter.is_convertible(23452345)

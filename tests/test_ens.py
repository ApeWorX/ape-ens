import pytest
from ape.api import NetworkAPI, Web3Provider
from ape.managers.networks import NetworkManager

from ape_ens.converters import ENSConversions


@pytest.fixture
def mock_networks(mocker):
    networks = mocker.MagicMock(spec=NetworkManager)
    mock_network = mocker.MagicMock(spec=NetworkAPI)
    mock_network.name = "mainnet"
    networks.active_provider = mocker.MagicMock(spec=Web3Provider)
    networks.active_provider.network = mock_network
    return networks


@pytest.fixture
def converter(mocker, mock_networks):
    return ENSConversions(
        config=mocker.MagicMock(), networks=mock_networks, converter=mocker.MagicMock()
    )


def test_is_convertible(converter):
    assert converter.is_convertible("test.eth")


def test_is_not_convertible(converter):
    assert not converter.is_convertible("test")
    assert not converter.is_convertible("0xe1122aa5533228143C4Ce8fC4642aa33b857B332")
    assert not converter.is_convertible(23452345)

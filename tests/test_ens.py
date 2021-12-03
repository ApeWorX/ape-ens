import pytest
from ape.api import ProviderAPI, Web3Provider
from ape.api.config import ConfigItem
from ape.exceptions import ProviderError
from ape.managers.networks import NetworkManager

from ape_ens.converters import ENSConversions


@pytest.fixture
def mock_networks(mocker):
    return mocker.MagicMock(spec=NetworkManager)


@pytest.fixture
def mock_config(mocker):
    return mocker.MagicMock(spec=ConfigItem)


def test_ens_when_no_provider(mock_config, mock_networks):
    mock_networks.active_provider = None

    with pytest.raises(ProviderError) as err:
        _ = ENSConversions(config=mock_config, networks=mock_networks).ens

    assert str(err.value) == "Not connected to a provider."


def test_ens_when_not_web3_provider(mocker, mock_config, mock_networks):
    mock_networks.active_provider = mocker.MagicMock(spec=ProviderAPI)

    with pytest.raises(NotImplementedError) as err:
        _ = ENSConversions(config=mock_config, networks=mock_networks).ens

    assert str(err.value) == "Currently, only web3 providers work with this plugin."


def test_is_convertible(mocker, mock_config, mock_networks):
    mock_networks.active_provider = mocker.MagicMock(spec=Web3Provider)
    converter = ENSConversions(config=mock_config, networks=mock_networks)
    assert converter.is_convertible("test.eth")
    assert not converter.is_convertible(23452345)

import ape
import pytest

from tests.conftest import negative_tests


@pytest.fixture
def connection_spy(mocker, converter):
    return mocker.spy(converter.network_manager, "get_provider_from_choice")


def test_is_convertible(converter):
    assert converter.is_convertible("test.eth")


@negative_tests
def test_is_not_convertible(converter, value):
    assert not converter.is_convertible(value)


def test_address_cache(converter, address):
    converter.address_cache["test.eth"] = address
    assert converter.convert("test.eth") == address


def test_mainnet_fork(converter, connection_spy):
    with ape.networks.parse_network_choice("ethereum:mainnet-fork:mock-mainnet-fork"):
        connection_spy.reset_mock()
        converter.convert("test.eth")

    # Should not have to reconnect
    assert not connection_spy.call_count


def test_other_ecosystem_mainnet(converter, connection_spy):
    with ape.networks.parse_network_choice("polygon:mainnet:mock-polygon-mainnet"):
        connection_spy.reset_mock()
        converter.convert("test.eth")

    # It has to re-connect to Ethereum mainnet temporarily
    connection_spy.assert_called_once_with("ethereum:mainnet")

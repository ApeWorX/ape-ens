import ape
from web3.exceptions import CannotHandleRequest

from tests.conftest import negative_tests


def test_is_convertible(converter):
    assert converter.is_convertible("test.eth")


@negative_tests
def test_is_not_convertible(converter, value):
    assert not converter.is_convertible(value)


def test_is_not_convertible_when_ens_address_call_fails(converter, mainnet_provider):
    """
    Tests against a bug where this would fail in an uncaught way rather
    than saying ``is_convertible=False``.
    """
    mainnet_provider.web3.ens.address.side_effect = CannotHandleRequest
    # NOTE: Using test2.eth since it should be free from the cache (not used elsewhere)
    assert not converter.is_convertible("test2.eth")


def test_address_cache(converter, address):
    converter.address_cache["test.eth"] = address
    assert converter.convert("test.eth") == address


def test_mainnet_fork(converter, mocker):
    get_eco_spy = mocker.spy(converter.network_manager, "get_ecosystem")

    with ape.networks.ethereum.mainnet_fork.use_provider("mock-mainnet-fork"):
        get_eco_spy.reset_mock()
        converter.convert("test.eth")

    # Should not have to reconnect
    assert not get_eco_spy.call_count


def test_other_ecosystem_mainnet(converter, mocker):
    get_eco_spy = mocker.spy(converter.network_manager, "get_ecosystem")

    with ape.networks.polygon.mainnet.use_provider("mock-polygon-mainnet"):
        get_eco_spy.reset_mock()
        converter.convert("test.eth")

    # It has to re-connect to Ethereum mainnet temporarily
    get_eco_spy.assert_called_once_with("ethereum")

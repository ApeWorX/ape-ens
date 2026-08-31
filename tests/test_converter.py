import pytest
from web3.exceptions import CannotHandleRequest

from tests.conftest import negative_tests


@pytest.fixture(autouse=True)
def clear_cache(converter):
    converter.address_cache = {}


def test_is_convertible_when_true(converter):
    assert converter.is_convertible("test.eth")


@negative_tests
def test_is_convertible_when_false(converter, value):
    assert not converter.is_convertible(value)


def test_is_convertible_when_ens_address_call_fails(converter, mock_web3_ens):
    """
    Tests against a bug where this would fail in an uncaught way rather
    than saying ``is_convertible=False``.
    """
    mock_web3_ens.address.side_effect = CannotHandleRequest
    assert not converter.is_convertible("please_fail.eth")


def test_convert(converter, vitalik):
    """
    Integration test: Actually connecting and converting here.
    """
    actual = converter.convert("vitalik.eth")
    assert actual == vitalik


def test_convert_on_local_uses_eth_coin_type(converter, mock_web3_ens, mocker):
    spy = mocker.spy(converter.ens, "resolve")
    converter.convert("vitalik.eth")
    spy.assert_called_with("vitalik.eth")
    mock_web3_ens.address.assert_called_with("vitalik.eth")


def test_convert_follows_connected_l2(trick_network, converter, mock_web3_ens, vitalik):
    with trick_network("mainnet", ecosystem="base"):
        actual = converter.convert("vitalik.eth")
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=2147492101)


def test_convert_when_connected_to_mainnet_fork(trick_network, converter, mock_web3_ens, vitalik):
    with trick_network("mainnet-fork"):
        actual = converter.convert("vitalik.eth")
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth")


def test_convert_when_connected_to_other_ecosystem_mainnet(
    trick_network, converter, mock_web3_ens, vitalik
):
    with trick_network("mainnet", ecosystem="polygon"):
        actual = converter.convert("vitalik.eth")
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=0x80000000 | 137)


def test_convert_using_config_registry(project, converter, vitalik, accounts):
    dev_account = accounts[0]
    ape_user = "apeconfig.eth"
    with project.temp_config(ens={"registry": {ape_user: dev_account.address}}):
        actual = converter.convert(ape_user)
        assert actual == dev_account.address


def test_convert_after_adding_to_local_registry(converter, vitalik, accounts):
    dev_account = accounts[0]
    ape_user = "apepython.eth"
    converter.ens.local_registry[ape_user] = dev_account.address
    actual = converter.convert(ape_user)
    assert actual == dev_account.address


def test_address_cache(converter, address):
    converter.address_cache["test.eth"] = address
    assert converter.convert("test.eth") == address

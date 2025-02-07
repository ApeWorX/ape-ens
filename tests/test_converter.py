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


def test_convert_when_connected_to_mainnet_fork(trick_network, converter, vitalik):
    trick_network("mainnet_fork")
    actual = converter.convert("vitalik.eth")
    assert actual == vitalik


def test_convert_when_connected_to_other_ecosystem_mainnet(trick_network, converter, vitalik):
    trick_network("polygon", ecosystem="polygon")
    actual = converter.convert("vitalik.eth")
    assert actual == vitalik


def test_address_cache(converter, address):
    converter.address_cache["test.eth"] = address
    assert converter.convert("test.eth") == address

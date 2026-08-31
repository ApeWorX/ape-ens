import pytest
from ens.exceptions import ResolverNotFound  # type: ignore[import-untyped]

from ape_ens.ens import ENS
from ape_ens.exceptions import (
    AmbiguousNetworkError,
    ConflictingResolveOptionsError,
    LocalNetworkCoinTypeError,
    UnknownNetworkError,
)
from ape_ens.utils.coin_type import DEFAULT_EVM_COIN_TYPE

BASE_COIN_TYPE = 2147492101  # 0x80000000 | 8453
BASE_SEPOLIA_COIN_TYPE = 0x80000000 | 84532


def test_resolve(ens, vitalik):
    assert ens.resolve("vitalik.eth") == vitalik


def test_resolve_forwards_coin_type(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", coin_type=BASE_COIN_TYPE, use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=BASE_COIN_TYPE)


def test_resolve_coin_type_does_not_use_eth_cache(ens, mock_web3_ens, address, vitalik):
    ens.local_registry["vitalik.eth"] = address
    actual = ens.resolve("vitalik.eth", coin_type=BASE_COIN_TYPE)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=BASE_COIN_TYPE)


def test_resolve_coin_type_60_matches_default_eth(ens, mock_web3_ens, address):
    ens.local_registry["vitalik.eth"] = address
    actual = ens.resolve("vitalik.eth", coin_type=60)
    assert actual == address
    mock_web3_ens.address.assert_not_called()
    assert "vitalik.eth:60" not in ens.local_registry


def test_resolve_coin_type_60_calls_default_address(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", coin_type=60, use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth")


def test_resolve_l2_falls_back_to_default_evm(ens, mock_web3_ens, address):
    def get_address(name, coin_type=None):
        if coin_type == DEFAULT_EVM_COIN_TYPE:
            return address
        return None

    mock_web3_ens.address.side_effect = get_address
    actual = ens.resolve("vitalik.eth", coin_type=BASE_COIN_TYPE, use_cache=False)
    assert actual == address
    mock_web3_ens.address.assert_any_call("vitalik.eth", coin_type=BASE_COIN_TYPE)
    mock_web3_ens.address.assert_any_call("vitalik.eth", coin_type=DEFAULT_EVM_COIN_TYPE)


def test_resolve_l2_does_not_fall_back_to_eth(ens, mock_web3_ens):
    mock_web3_ens.address.side_effect = lambda name, coin_type=None: None
    actual = ens.resolve("vitalik.eth", coin_type=BASE_COIN_TYPE, use_cache=False)
    assert actual is None
    assert mock_web3_ens.address.call_count == 2
    for call in mock_web3_ens.address.call_args_list:
        assert call.kwargs.get("coin_type") in (BASE_COIN_TYPE, DEFAULT_EVM_COIN_TYPE)


def test_resolve_infers_connected_l2(ens, mock_web3_ens, vitalik, trick_network):
    with trick_network("mainnet", ecosystem="base"):
        actual = ens.resolve("vitalik.eth", use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=BASE_COIN_TYPE)


def test_resolve_ape_network_ethereum_mainnet(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", ecosystem="ethereum", network="mainnet", use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth")


def test_resolve_ape_network_base_mainnet(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", ecosystem="base", network="mainnet", use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=BASE_COIN_TYPE)


def test_resolve_ape_network_base_shorthand(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", network="base", use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=BASE_COIN_TYPE)


def test_resolve_ape_network_combined_choice(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", network="base:mainnet", use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=BASE_COIN_TYPE)


def test_resolve_ape_network_ecosystem_only_uses_mainnet(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", ecosystem="base", use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=BASE_COIN_TYPE)


def test_resolve_ape_network_mainnet_fork_uses_upstream_eth(ens, mock_web3_ens, vitalik):
    actual = ens.resolve(
        "vitalik.eth", ecosystem="ethereum", network="mainnet-fork", use_cache=False
    )
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth")


def test_resolve_ape_network_ethereum_sepolia_uses_eth_coin_type(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", ecosystem="ethereum", network="sepolia", use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth")


def test_resolve_ape_network_base_sepolia_uses_ensip11(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", ecosystem="base", network="sepolia", use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=BASE_SEPOLIA_COIN_TYPE)


def test_resolve_ape_network_three_part_choice_ignores_provider(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", network="base:mainnet:node", use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=BASE_COIN_TYPE)


def test_resolve_ape_network_base_mainnet_fork_uses_upstream(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", ecosystem="base", network="mainnet-fork", use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=BASE_COIN_TYPE)


def test_match_network_name_hyphen_underscore_are_aliases(ens):
    hyphen = ens._match_network_name("mainnet-fork")
    underscore = ens._match_network_name("mainnet_fork")
    assert hyphen
    assert len(hyphen) == len({eco for eco, _ in hyphen})
    assert set(hyphen) == set(underscore)


def test_resolve_rejects_coin_type_and_network(ens):
    with pytest.raises(ConflictingResolveOptionsError):
        ens.resolve("vitalik.eth", coin_type=60, ecosystem="base")


def test_resolve_network_mainnet_is_ambiguous(ens):
    with pytest.raises(AmbiguousNetworkError, match="ambiguous"):
        ens.resolve("vitalik.eth", network="mainnet")


def test_resolve_local_network_coin_type(ens):
    with pytest.raises(LocalNetworkCoinTypeError):
        ens.resolve("vitalik.eth", ecosystem="ethereum", network="local")


def test_resolve_unknown_ape_network(ens):
    with pytest.raises(UnknownNetworkError, match="Unknown Ape ecosystem or network"):
        ens.resolve("vitalik.eth", network="not-a-real-chain-xyz")


def test_resolve_unknown_ecosystem(ens):
    with pytest.raises(UnknownNetworkError):
        ens.resolve("vitalik.eth", ecosystem="not-an-eco-xyz")


def test_resolve_unknown_network_in_ecosystem(ens):
    with pytest.raises(UnknownNetworkError):
        ens.resolve("vitalik.eth", ecosystem="ethereum", network="not-a-net-xyz")


def test_get_text(ens, mock_web3_ens):
    mock_web3_ens.get_text.return_value = "Blockchain & Backend Developer"
    assert ens.get_text("vitalik.eth", "description") == "Blockchain & Backend Developer"
    mock_web3_ens.get_text.assert_called_once_with("vitalik.eth", "description")


def test_get_text_empty(ens, mock_web3_ens):
    mock_web3_ens.get_text.return_value = ""
    assert ens.get_text("vitalik.eth", "url") is None


def test_get_text_resolver_not_found(ens, mock_web3_ens):
    mock_web3_ens.get_text.side_effect = ResolverNotFound("missing")
    assert ens.get_text("missing.eth", "url") is None


def test_create_web3_ens_uses_configured_registry_address(project, accounts, mocker):
    fake_registry = accounts[0].address
    mock_backend = mocker.MagicMock()
    from_web3 = mocker.patch("ape_ens.ens.Web3ENS.from_web3", return_value=mock_backend)

    with project.temp_config(ens={"registry_address": fake_registry}):
        wrapper = ENS()
        wrapper.__dict__["_mainnet_provider"] = mocker.MagicMock()
        actual = wrapper._create_web3_ens()

    assert actual is mock_backend
    assert from_web3.call_args.args[1] == fake_registry

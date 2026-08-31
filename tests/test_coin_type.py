from ape_ens.utils.coin_type import DEFAULT_EVM_COIN_TYPE, ETH_COIN_TYPE, coin_type_from_chain_id


def test_coin_type_from_chain_id_ethereum_is_slip44():
    assert coin_type_from_chain_id(1) == ETH_COIN_TYPE == 60


def test_coin_type_from_chain_id_ethereum_l1_testnets_are_slip44():
    assert coin_type_from_chain_id(11155111) == ETH_COIN_TYPE  # sepolia
    assert coin_type_from_chain_id(17000) == ETH_COIN_TYPE  # holesky
    assert coin_type_from_chain_id(560048) == ETH_COIN_TYPE  # hoodi


def test_coin_type_from_chain_id_ensip11_l2():
    assert coin_type_from_chain_id(8453) == (0x80000000 | 8453)
    assert coin_type_from_chain_id(8453) == 2147492101


def test_coin_type_from_chain_id_l2_testnet_is_ensip11():
    assert coin_type_from_chain_id(84532) == (0x80000000 | 84532)  # base sepolia


def test_coin_type_from_chain_id_polygon():
    assert coin_type_from_chain_id(137) == (0x80000000 | 137)


def test_default_evm_coin_type():
    assert DEFAULT_EVM_COIN_TYPE == 0x80000000

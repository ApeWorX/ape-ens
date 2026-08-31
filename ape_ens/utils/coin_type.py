ETH_COIN_TYPE = 60
EVM_COIN_TYPE_OFFSET = 0x80000000
# ENSIP-19: chainId 0 — "any EVM" fallback when a chain-specific record is unset.
DEFAULT_EVM_COIN_TYPE = EVM_COIN_TYPE_OFFSET

# ENSIP-19: coin type 60 is the Ethereum address. L1 testnets (Sepolia, etc.)
# use the same coin type, not ``0x80000000 | chain_id``.
ETH_L1_CHAIN_IDS = frozenset(
    {
        1,  # mainnet
        5,  # goerli
        17000,  # holesky
        560048,  # hoodi
        11155111,  # sepolia
    }
)


def coin_type_from_chain_id(chain_id: int) -> int:
    """Map an EVM chain ID to an ENSIP-9/11 coin type.

    Ethereum L1 (mainnet and its testnets) is SLIP-44 coin 60, not
    ``0x80000000 | chain_id``. Other EVM chains use ENSIP-11:
    ``0x80000000 | chain_id``.
    """
    if chain_id in ETH_L1_CHAIN_IDS:
        return ETH_COIN_TYPE
    return EVM_COIN_TYPE_OFFSET | chain_id

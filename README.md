# Quick Start

Ape plugin for ENS argument conversion and contracts

## Dependencies

- [python3](https://www.python.org/downloads) version 3.9 up to 3.12.

## Installation

### via `pip`

You can install the latest release via [`pip`](https://pypi.org/project/pip/):

```bash
pip install ape-ens
```

### via `setuptools`

You can clone the repository and use [`setuptools`](https://github.com/pypa/setuptools) for the most up-to-date version:

```bash
git clone https://github.com/ApeWorX/ape-ens.git
cd ape-ens
python3 setup.py install
```

## Quick Usage

Ensure you are satisfied with your Ethereum mainnet setup in Ape, as this plugin requires a connection to Ethereum to resolve ENS domains.
More information on networks can be found in [Ape's network guide](https://docs.apeworx.io/ape/stable/userguides/networks.html#networks).

If using Ape and not connected to mainnet, `ape-ens` will temporarily connect to Ethereum mainnet to resolve addresses, using your default mainnet provider.

To configure a default mainnet provider, do:

```yaml
ethereum:
  mainnet:
    default_provider: alchemy  # Example, you can use any mainnet provider
```

Otherwise, the plugin should still work with Ape's defaults, using an RPC from the `evmchains` library.

This plugin contains two features:

- A conversion API implementation: this allows you to use ENS values in contract calls and transaction kwargs.
- a CLI for interacting with ENS from the command line.

### Conversion API

When this plugin is installed, you can use ENS names in contract-calls, and they resolve to the addresses automatically:

```python
from ape import accounts, Contract

ens_name = "vitalik.eth"  # Going to use this later...
contract = Contract("0x123...")
me = accounts.load("me")

# Ape resolves "me" to my account's address and "vitalik.eth" to Vitalik's Ethereum address.
# It is thanks to the ape-ens plugin that "vitalik.eth" works as a transaction input.
contract.transferFrom(me, ens_name, 100, sender=me)
```

You can use Ape's conversion utility directly:

```python
from ape import convert
from ape.types import AddressType

convert("vitalik.eth", AddressType)
# returns: '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045'
```

Additionally, you can get the Ethereum Name Service (ENS) namehash using the `namehash` function:

```py
from ape_ens.utils import namehash

namehash("eth").hex()
# "0x93cdeb708b7545dc668eb9280176169d1c33cfd8ed6f04690a0bcc88a93fc4ae"

namehash("foo.eth")
# HexBytes("0xde9b09fd7c5f901e23a3f19fecc54828e9c848539801e86591bd9801b019f84f")

namehash("ape.rocks.eth").hex()
# "0x6294e43e29c5c1573554a68e6ff302fa867ab0d56b800f623c1abb77609d2b8d"
```

### CLI

`ape-ens` comes with a CLI for using ENS.

Resolve ENS domains from the command line:

```shell
ape ens resolve vitalik.eth
# outputs: 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

Reverse-lookup an ENS domain:

```shell
ape ens name 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
# outputs: vitalik.eth
```

Get the owner of an ENS domain:

```shell
ape ens owner vitalik.eth
# outputs: 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

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

This plugin contains two primary features:

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

namehash("foo.eth")
# HexBytes("0xde9b09fd7c5f901e23a3f19fecc54828e9c848539801e86591bd9801b019f84f")
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

Get the namehash of an ENS name:

```shell
ape ens namehash foo.eth
# outputs: 0xde9b09fd7c5f901e23a3f19fecc54828e9c848539801e86591bd9801b019f84f
```

### Using `ape-ens` as a library.

You can also use the `ape_ens.ENS` class directly for programmatically referring to ENS.

```python
from ape_ens import ENS

ens = ENS()
vitalik = ens.resolve("vitalik.eth")
print(vitalik)
```

### Local registry

**WARNING**: By default, `ape-ens` caches results during each Python session for faster name resolution in scripts and testing.
Be careful using ENS names in long-running scripts where it would be bad if the name resolved differently in the future.
To disable caching, configure `ape-ens` to always read from Ethereum by adding to your `pyproject.toml`:

```toml
[tool.ape.ens]
use_cache = false
```

or using `ape-config.yaml`:

```yaml
ens:
  use_cache: false
```

To manually add entries to the cache, you can include them under the `registry:` key in the config:

```toml
[tool.ape.ens]
registry = { vitalik.eth = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045" }
```

or using `ape-config.yaml`:

```yaml
ens:
  registry:
    vitalik.eth: "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
```

Configuring entries is useful for:

1. Testing in the `local` network.
2. Attaining faster performance (no Ethereum call).
3. Avoiding connecting to Ethereum mainnet.

### Change Registry

Change the registry contract address by configuring it in your `pyproject.toml`:

```toml
[tool.ape.ens]
registry_address = "0x123..."
```

or using `ape-config.yaml`:

```yaml
ens:
  registry_address: "0x123..."
```

You can also switch the registry adhoc during CLI commands:

```shell
ape ens resolve vitalik.eth --registry-address 0x123...311
```

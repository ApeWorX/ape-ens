# Ape ENS Plugin

Ape plugin for ENS argument conversion and contracts

## Dependencies

* [python3](https://www.python.org/downloads) version 3.7 or greater, python3-dev

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

First, start the ape console using the network of your choice:

```bash
ape console --network :mainnet:infura
```

Then, convert an `ens` domain to an `AddressType`:

```python
In [1]: from ape.types import AddressType
In [2]: convert("vitalik.eth", AddressType)
Out[2]: '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045'
```

## Development

This project is in development and should be considered a beta.
Things might not be in their final state and breaking changes may occur.
Comments, questions, criticisms and pull requests are welcomed.

## License

This project is licensed under the [Apache 2.0](LICENSE).

from functools import cached_property

import click
from ape.cli import ApeCliContextObject, ape_cli_context, network_option
from ape.exceptions import ConversionError, NetworkError
from ape.types.address import AddressType
from eth_utils import to_hex

from ape_ens.ens import ENS
from ape_ens.exceptions import ApeENSException


def create_ens() -> ENS:
    # Abstracted for testing purposes.
    return ENS()


class ENSContext(ApeCliContextObject):
    @cached_property
    def ens(self) -> ENS:
        return create_ens()


@click.group()
def cli():
    """
    ENS commands.
    """


def registry_address_option(**kwargs):
    if "callback" not in kwargs:

        def validate_address(ctx, param, value):
            if value is None:
                return value

            from ape import convert

            try:
                return convert(value, AddressType)
            except ConversionError:
                raise click.BadOptionUsage(
                    "--registry-address", f"Invalid `--registry-address` {value}."
                )

        kwargs["callback"] = validate_address

    if "help" not in kwargs:
        kwargs["help"] = "ENS registry address"

    return click.option("--registry-address", **kwargs)


def coin_type_option(**kwargs):
    if "help" not in kwargs:
        kwargs["help"] = "ENSIP-9/11 coin type for multichain resolution. Defaults to ETH (60)."

    return click.option("--coin-type", type=int, default=None, **kwargs)


def ens_ecosystem_option(**kwargs):
    if "help" not in kwargs:
        kwargs["help"] = "Ape ecosystem for ENSIP-11 coin type (e.g. base)."

    return click.option("--ens-ecosystem", default=None, **kwargs)


def ens_network_option(**kwargs):
    if "help" not in kwargs:
        kwargs["help"] = (
            "Override ENS coin type using an Ape network (e.g. mainnet or base:mainnet). "
            "A trailing :provider is ignored. Default follows --network (connected chain). "
            "L2s use that chain's record, then default EVM, not ETH (60)."
        )

    return click.option("--ens-network", default=None, **kwargs)


@cli.command()
@ape_cli_context(obj_type=ENSContext)
@click.argument("name")
@network_option(default=None)
@registry_address_option()
@coin_type_option()
@ens_ecosystem_option()
@ens_network_option()
def resolve(cli_ctx, name, registry_address, coin_type, ens_ecosystem, ens_network):
    """
    Resolve an ENS address.
    """
    try:
        address = cli_ctx.ens.resolve(
            name,
            registry_address=registry_address,
            coin_type=coin_type,
            ecosystem=ens_ecosystem,
            network=ens_network,
        )
    except (ApeENSException, NetworkError) as err:
        raise click.UsageError(str(err)) from err

    if address:
        click.echo(address)
    else:
        click.echo(f"Could not resolve ENS '{name}'.", err=True)


@cli.command(name="name")
@ape_cli_context(obj_type=ENSContext)
@click.argument("address")
@network_option(default=None)
@registry_address_option()
def name_cmd(cli_ctx, address, registry_address):
    """
    Get the ENS of an address.
    """
    if name := cli_ctx.ens.name(address, registry_address=registry_address):
        click.echo(name)
    else:
        click.echo(f"No ENS name found for '{address}'.", err=True)


@cli.command()
@ape_cli_context(obj_type=ENSContext)
@click.argument("name")
@network_option(default=None)
@registry_address_option()
def owner(cli_ctx, name, registry_address):
    """
    Get the ENS registry owner of a domain.
    """
    if owner_address := cli_ctx.ens.owner(name, registry_address=registry_address):
        click.echo(owner_address)
    else:
        click.echo(f"No owner found for '{name}'.", err=True)


@cli.command()
@ape_cli_context(obj_type=ENSContext)
@click.argument("name")
@click.argument("key")
@network_option(default=None)
@registry_address_option()
def text(cli_ctx, name, key, registry_address):
    """
    Get an ENS text record.
    """
    if value := cli_ctx.ens.get_text(name, key, registry_address=registry_address):
        click.echo(value)
    else:
        click.echo(f"No text record '{key}' found for '{name}'.", err=True)


@cli.command()
@ape_cli_context(obj_type=ENSContext)
@click.argument("name")
@network_option(default=None)
def namehash(cli_ctx, name):
    """
    Get the namehash of an ENS domain.
    """
    name_hash = cli_ctx.ens.namehash(name)
    name_hex = to_hex(name_hash)
    click.echo(name_hex)

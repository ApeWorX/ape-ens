from functools import cached_property

import click
from ape.cli import ApeCliContextObject, ape_cli_context, network_option
from ape.exceptions import ConversionError
from ape.types.address import AddressType
from eth_utils import to_hex

from ape_ens.ens import ENS


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


@cli.command()
@ape_cli_context(obj_type=ENSContext)
@click.argument("name")
@network_option(default=None)
@registry_address_option()
def resolve(cli_ctx, name, registry_address):
    """
    Resolve an ENS address.
    """
    if address := cli_ctx.ens.resolve(name, registry_address=registry_address):
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
    Get the owner of an ENS domain.
    """
    if owner_address := cli_ctx.ens.owner(name, registry_address=registry_address):
        click.echo(owner_address)
    else:
        click.echo(f"No owner found for '{name}'.", err=True)


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

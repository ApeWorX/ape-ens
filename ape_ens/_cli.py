from functools import cached_property

import click
from ape.cli import ApeCliContextObject, ape_cli_context, network_option

from ape_ens.ens import ENS


def create_ens():
    # Abstracted for testing purposes.
    return ENS()


class ENSContext(ApeCliContextObject):
    @cached_property
    def ens(self):
        return create_ens()


@click.group()
def cli():
    """
    ENS commands.
    """


@cli.command()
@ape_cli_context(obj_type=ENSContext)
@click.argument("name")
@network_option(default=None)
def resolve(cli_ctx, name):
    """
    Resolve an ENS address.
    """
    if address := cli_ctx.ens.resolve(name):
        click.echo(address)
    else:
        click.echo(f"Could not resolve ENS '{name}'.", err=True)


@cli.command(name="name")
@ape_cli_context(obj_type=ENSContext)
@click.argument("address")
@network_option(default=None)
def name_cmd(cli_ctx, address):
    """
    Get the ENS of an address.
    """
    if name := cli_ctx.ens.name(address):
        click.echo(name)
    else:
        click.echo(f"No ENS name found for '{address}'.", err=True)


@cli.command()
@ape_cli_context(obj_type=ENSContext)
@click.argument("name")
@network_option(default=None)
def owner(cli_ctx, name):
    """
    Get the owner of an ENS domain.
    """
    if owner_address := cli_ctx.ens.owner(name):
        click.echo(owner_address)
    else:
        click.echo(f"No owner found for '{name}'.", err=True)

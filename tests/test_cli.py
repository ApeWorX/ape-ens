import pytest
from click.testing import CliRunner

from ape_ens._cli import cli


@pytest.fixture(autouse=True)
def setup_ens(mocker, ens):
    patch = mocker.patch("ape_ens._cli.create_ens")
    patch.return_value = ens


@pytest.fixture
def runner():
    return CliRunner()


def test_resolve(networks, runner):
    result = runner.invoke(cli, ["resolve", "vitalik.eth"])
    assert "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045" in result.output, result.output


def test_name(runner):
    result = runner.invoke(cli, ["name", "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"])
    assert "vitalik.eth" in result.output, result.output


def test_owner(runner):
    result = runner.invoke(cli, ["owner", "vitalik.eth"])
    assert "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045" in result.output, result.output

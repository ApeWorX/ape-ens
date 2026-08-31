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


def test_resolve(runner):
    result = runner.invoke(cli, ["resolve", "vitalik.eth"])
    assert "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045" in result.output, result.output


def test_resolve_invalid_registry_address(runner):
    result = runner.invoke(cli, ["resolve", "vitalik.eth", "--registry-address", "asdf"])
    assert result.exit_code != 0


def test_name(runner):
    result = runner.invoke(cli, ["name", "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"])
    assert "vitalik.eth" in result.output, result.output


def test_owner(runner):
    result = runner.invoke(cli, ["owner", "vitalik.eth"])
    assert "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045" in result.output, result.output


def test_namehash(runner):
    result = runner.invoke(cli, ["namehash", "foo.eth"])
    expected = "0xde9b09fd7c5f901e23a3f19fecc54828e9c848539801e86591bd9801b019f84f"
    assert expected in result.output, result.output


def test_resolve_coin_type(runner, mock_web3_ens):
    result = runner.invoke(cli, ["resolve", "vitalik.eth", "--coin-type", "2147492101"])
    assert "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045" in result.output, result.output
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=2147492101)


def test_resolve_ens_ecosystem_network(runner, mock_web3_ens):
    result = runner.invoke(
        cli,
        ["resolve", "vitalik.eth", "--ens-ecosystem", "base", "--ens-network", "mainnet"],
    )
    assert "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045" in result.output, result.output
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=2147492101)


def test_resolve_ens_network_shorthand(runner, mock_web3_ens):
    result = runner.invoke(cli, ["resolve", "vitalik.eth", "--ens-network", "base"])
    assert "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045" in result.output, result.output
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=2147492101)


def test_resolve_ens_network_three_part_choice(runner, mock_web3_ens):
    result = runner.invoke(cli, ["resolve", "vitalik.eth", "--ens-network", "base:mainnet:node"])
    assert "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045" in result.output, result.output
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=2147492101)


def test_resolve_coin_type_and_ens_network_conflict(runner):
    result = runner.invoke(
        cli,
        ["resolve", "vitalik.eth", "--coin-type", "60", "--ens-network", "base"],
    )
    assert result.exit_code != 0
    assert "Cannot pass coin_type together with ecosystem or network" in result.output


def test_text(runner, mock_web3_ens):
    mock_web3_ens.get_text.return_value = "https://vitalik.ca"
    result = runner.invoke(cli, ["text", "vitalik.eth", "url"])
    assert "https://vitalik.ca" in result.output, result.output
    mock_web3_ens.get_text.assert_called_once_with("vitalik.eth", "url")


def test_text_missing(runner, mock_web3_ens):
    mock_web3_ens.get_text.return_value = ""
    result = runner.invoke(cli, ["text", "vitalik.eth", "url"])
    assert "No text record 'url' found for 'vitalik.eth'." in result.output

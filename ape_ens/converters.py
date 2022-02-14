from pathlib import Path
from typing import Any

from ape.api import ConfigDict, ConfigItem, ConverterAPI
from ape.types import AddressType
from ape.utils import cached_property
from ethpm_types import PackageManifest

from .utils import get_node_id

# TODO: Store/Load from IPFS
ENS_PACKAGE = PackageManifest.parse_file(Path(__file__).parent / "ens-manifest.json")


class ENSConfig(ConfigItem):
    provider_name: str = "geth"
    provider_settings: ConfigDict = {}  # type: ignore


class ENSConversions(ConverterAPI):
    """Converts ENS names like `my-name.eth` to `0xAbCd...1234`"""

    @cached_property
    def registrar(self):
        from ape import Contract

        # NOTE: ENS Only references data from Ethereum Mainnet
        registrar_deployment = list(ENS_PACKAGE.deployments.values())[0]["Registrar"]
        with self.networks.ethereum.mainnet.use_provider(
            self.config.provider_name,
            self.config.provider_settings,
        ):
            return Contract(
                address=registrar_deployment.address,
                contract_type=ENS_PACKAGE.Registrar,
            )

    def is_convertible(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        elif "." not in value:
            # NOTE: ENS names always have a root
            return False

        else:
            return self.registrar.resolver(get_node_id(value))

    def convert(self, value: str) -> AddressType:
        from ape import Contract

        node_id = get_node_id(value)
        resolver = Contract(
            self.registrar.resolver(node_id),
            contract_type=ENS_PACKAGE.Resolver,
        )
        return resolver.addr(node_id)  # type: ignore

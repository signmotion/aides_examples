from ..share.config import *
from ..share.context import Context, test_context_smarthone
from ..share.packages.aide_server.src.aide_server.configure import Configure
from ..share.packages.aide_server.src.aide_server.keeper_brokers.filesystem import (
    FilesystemKeeperBroker,
)
from ..share.packages.aide_server.src.aide_server.server import AideServer, Memo


with open("kins/share/configure.json", "r") as file:
    configure = Configure.model_validate_json(file.read())


class Keeper(AideServer):
    def __init__(self):
        super().__init__(
            language="en",
            configure=configure,
            keeper_broker=FilesystemKeeperBroker(path_prefix="local_storage"),
            memo=Memo(test_context_smarthone() if use_test_context else Context()),
        )

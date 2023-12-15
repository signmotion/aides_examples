from ..share.config import *
from ..share.packages.aide_server.src.aide_server.configure import Configure
from ..share.packages.aide_server.src.aide_server.inner_memo import InnerMemo
from ..share.packages.aide_server.src.aide_server.memo_brokers.filesystem import (
    FilesystemMemoBroker,
)
from ..share.packages.aide_server.src.aide_server.server import AideServer


with open("kins/share/configure.json", "r") as file:
    configure = Configure.model_validate_json(file.read())


class Keeper(AideServer):
    def __init__(self):
        super().__init__(
            configure=configure,
            inner_memo=InnerMemo(
                FilesystemMemoBroker(path_prefix="keeper_inner_memo"),
            ),
        )

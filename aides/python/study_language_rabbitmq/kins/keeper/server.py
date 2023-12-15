from ..share.config import *
from ..share.packages.aide_server.src.aide_server.inner_memo import InnerMemo
from ..share.packages.aide_server.src.aide_server.memo_brokers.filesystem import (
    FilesystemMemoBroker,
)
from ..share.packages.aide_server.src.aide_server.server import AideServer


class Keeper(AideServer):
    def __init__(self):
        super().__init__(
            inner_memo=InnerMemo(FilesystemMemoBroker(path_prefix="keeper_inner_memo")),
        )

from ..share.config import *
from ..share.context import Context, test_context_registered_aides_init
from ..share.packages.aide_server.src.aide_server.context_memo import ContextMemo
from ..share.packages.aide_server.src.aide_server.memo_brokers.filesystem import (
    FilesystemMemoBroker,
)
from ..share.packages.aide_server.src.aide_server.server import AideServer


class Appearance(AideServer):
    def __init__(self):
        super().__init__(
            context_memo=ContextMemo(
                test_context_registered_aides_init() if use_test_context else Context(),
                broker=FilesystemMemoBroker("memo/appearance_context"),
            ),
        )

from ..share.config import use_test_context
from ..share.context import Context, test_context_init
from ..share.packages.aide_server.src.aide_server.context_memo import ContextMemo
from ..share.packages.aide_server.src.aide_server.memo_brokers.filesystem import (
    FilesystemMemoBroker,
)
from ..share.packages.aide_server.src.aide_server.server import AideServer


class Appearance(AideServer):
    def __init__(self):
        super().__init__(
            context_memo=ContextMemo(
                broker=FilesystemMemoBroker("memo/appearance_context"),
                context=test_context_init() if use_test_context else Context(),
            ),
        )

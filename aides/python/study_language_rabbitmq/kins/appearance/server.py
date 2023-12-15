from ..share.config import *
from ..share.context import Context, test_context_article
from ..share.packages.aide_server.src.aide_server.context_memo import ContextMemo
from ..share.packages.aide_server.src.aide_server.inner_memo import InnerMemo
from ..share.packages.aide_server.src.aide_server.memo_brokers.filesystem import (
    FilesystemMemoBroker,
)
from ..share.packages.aide_server.src.aide_server.memo_brokers.shelve import (
    ShelveMemoBroker,
)
from ..share.packages.aide_server.src.aide_server.server import AideServer


class Appearance(AideServer):
    def __init__(self):
        super().__init__(
            inner_memo=InnerMemo(ShelveMemoBroker("appearance_inner_memo")),
            context_memo=ContextMemo(
                test_context_article() if use_test_context else Context(),
                broker=FilesystemMemoBroker("appearance_context_memo"),
            ),
        )

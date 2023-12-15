from ..share.config import *
from ..share.packages.aide_server.src.aide_server.server import (
    AideServer,
)
from ..share.routes.phrasal_verbs import phrasal_verbs


class Brain(AideServer):
    def __init__(self):
        super().__init__(
            brain_runs=[phrasal_verbs],
        )

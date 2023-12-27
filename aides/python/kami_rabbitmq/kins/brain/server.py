from ..share.config import *
from ..share.packages.aide_server.src.aide_server.server import AideServer
from ..share.acts.who_and_how_can_help import who_and_how_can_help


class Brain(AideServer):
    def __init__(self):
        super().__init__(
            brain_runs=[who_and_how_can_help],
        )

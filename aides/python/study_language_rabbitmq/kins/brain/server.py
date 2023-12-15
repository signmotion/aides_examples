from ..share.config import *
from ..share.packages.aide_server.src.aide_server.configure import Configure
from ..share.packages.aide_server.src.aide_server.server import (
    AideServer,
)
from ..share.routes.phrasal_verbs import phrasal_verbs


with open("kins/share/configure.json", "r") as file:
    configure = Configure.model_validate_json(file.read())


class Brain(AideServer):
    def __init__(self):
        super().__init__(
            configure=configure,
            brain_runs=[phrasal_verbs],
        )

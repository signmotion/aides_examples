from ..share.config import *
from ..share.packages.aide_server.src.aide_server.configure import Configure
from ..share.packages.aide_server.src.aide_server.server import (
    AideServer,
)
from ..share.routers.products_today import products_today


with open("kins/share/configure.json", "r") as file:
    configure = Configure.model_validate_json(file.read())


class Brain(AideServer):
    def __init__(self):
        super().__init__(
            configure=configure,
            brain_runs=[products_today],
        )

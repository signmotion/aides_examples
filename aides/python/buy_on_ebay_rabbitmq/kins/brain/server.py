from ..share.config import *
from ..share.packages.aide_server.src.aide_server.server import AideServer
from ..share.acts.products_today import products_today


class Brain(AideServer):
    def __init__(self):
        super().__init__(
            brain_runs=[products_today],
        )

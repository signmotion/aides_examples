from ..share.config import *
from ..share.context import Context, test_context_smarthone
from ..share.packages.aide_server.src.aide_server.configure import Configure
from ..share.packages.aide_server.src.aide_server.server import AideServer, Memo
from ..share.routers.products_today import products_today


with open("kins/share/configure.json", "r") as file:
    configure = Configure.model_validate_json(file.read())


class Appearance(AideServer):
    def __init__(self):
        super().__init__(
            language="en",
            configure=configure,
            brain_runs=[
                products_today,
            ],
            memo=Memo(test_context_smarthone() if use_test_context else Context()),
        )

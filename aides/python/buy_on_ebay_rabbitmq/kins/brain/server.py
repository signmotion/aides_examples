from ..share.config import *
from ..share.context import Context, test_context_smarthone
from ..share.packages.aide_server.src.aide_server.configure import Configure
from ..share.packages.aide_server.src.aide_server.server import AideServer, Memo


with open("kins/share/configure.json", "r") as file:
    configure = Configure.model_validate_json(file.read())


class Brain(AideServer):
    def __init__(self: AideServer):
        super().__init__(
            language="en",
            configure=configure,
            memo=Memo(test_context_smarthone() if use_test_context else Context()),
        )

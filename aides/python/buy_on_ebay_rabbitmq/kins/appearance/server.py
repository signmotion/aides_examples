from calendar import c

from kins.share.packages.aide_server.src.aide_server.configure import Configure
from ..share.config import *
from ..share.context import Context, test_context_smarthone
from ..share.packages.aide_server.src.aide_server.server import AideServer, Memo
from .routers import products_today


with open("kins/share/configure.json", "r") as file:
    configure = Configure.model_validate_json(file.read())


class Appearance(AideServer):
    def __init__(self: AideServer):
        super().__init__(
            language="en",
            configure=configure,
            memo=Memo(test_context_smarthone() if use_test_context else Context()),
            external_routers=[
                products_today.router(
                    api_domain=api_domain,
                    ebay_oauth_app_token=ebay_oauth_app_token,
                    is_production=is_production,
                    use_fake_response=use_fake_response,
                    include_original_response_in_response=include_original_response_in_response,
                ),
            ],
        )

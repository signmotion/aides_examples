from fastapi import APIRouter, FastAPI, routing
import logging
import os
from pydantic import Field
from typing import Callable, List

from .configure import Configure
from .context_memo import ContextMemo, NoneContextMemo
from .helpers import unwrap_multilang_text_list, skip_check_route
from .inner_memo import InnerMemo, NoneInnerMemo
from .log import logger
from .memo_brokers.filesystem import FilesystemMemoBroker
from .savant_router import SavantRouter
from .sides.appearance_side import AppearanceSide
from .sides.brain_side import BrainSide
from .sides.keeper_side import KeeperSide
from .sides.side import Side


class AideServer(FastAPI):
    """
    Aide Server.
    """

    def __init__(
        self,
        *,
        path_to_configure: str = "kins/share/configure.json",
        brain_runs: List[Callable] = [],
        context_memo: ContextMemo = NoneContextMemo(),
        inner_memo: InnerMemo = NoneInnerMemo(),
        language: str = "en",
        debug_level: int = logging.INFO,
    ):
        logging.basicConfig(level=debug_level)

        with open(path_to_configure, "r") as file:
            configure = Configure.model_validate_json(file.read())

        tags = unwrap_multilang_text_list(configure.tags, language=language)
        openapi_tags = []
        if bool(tags):
            openapi_tags.append(
                {
                    "name": "tags",
                    "value": tags,
                }
            )

        if configure.characteristic:
            openapi_tags.append(
                {
                    "name": "characteristic",
                    "value": configure.characteristic,
                }
            )

        sidename = type(self).__name__.lower()

        name = configure.name.get(language) or "Aide Server"
        savant_router = SavantRouter(
            configure.savant_connector,
            hid_server=configure.hid,
            sidename_server=sidename,
            acts=configure.acts,
        )

        super().__init__(
            title=name,
            summary=configure.summary.get(self.language),
            description=configure.description.get(self.language) or "",
            version=configure.version,
            openapi_tags=openapi_tags,
            lifespan=savant_router.lifespan_context,
        )

        self.language = language
        self.name = name
        self.sidename = sidename
        self.tags = tags
        self.configure = configure
        self.brain_runs = brain_runs
        self.inner_memo = inner_memo
        self.context_memo = context_memo
        self.savant_router = savant_router

        self.register_side()
        self.declare_channels()

    def register_side(self):
        logger.info(f"🏳️‍🌈 Initializing the side `{self.sidename}`...")

        # adding runs, endpoint and catchers for its as external routes
        router = APIRouter()
        self.side = self.build_side(router)

        logger.info(f"🏳️‍🌈 Initialized the side `{self.sidename}`.")

        self.include_router(router)
        logger.info(f"🍁 Included the router to the side `{self.sidename}`.")

        # !) call this functions after adding all routes
        # self._check_routes()
        # self._use_route_names_as_operation_ids()

        logger.info(f"🪶 Registered the side `{self.sidename}`.")

    def declare_channels(self):
        logger.info("🌱 Declaring the channels...")

        @self.savant_router.after_startup
        async def app_started(app: AideServer):
            await self.savant_router.declare_exchange()
            await self.savant_router.declare_service_queues()
            await self.savant_router.declare_acts_queues()

            message = (
                f"🚩 `{self.sidename}` `{self.hid}` started"
                " and powered by FastStream & FastAPI."
            )
            logger.info(message)

            logger.info(
                f"😎 Testing connection to Savant `{self.savant_router.broker.url}`"
                f" from `{self.sidename}` `{self.hid}`..."
            )
            await self.savant_router.broker.publish(
                message,
                queue=self.savant_router.logQueue(
                    pusher_side=self.side.type,
                    catcher_side=self.side.type,
                ),
                exchange=self.savant_router.exchange(),
                # need for production
                timeout=6,
            )

        @self.savant_router.broker.subscriber(
            self.savant_router.logQueue(
                pusher_side=self.side.type,
                catcher_side=self.side.type,
            ),
            self.savant_router.exchange(),
        )
        async def check_connection_to_savant(message: str):
            logger.info(
                "😎 Connection to Savant"
                f" from `{self.sidename}` `{self.hid}` confirmed."
                # f' Message received: "{message[:24]}...{message[-12:]}"'
            )

        logger.info("🌱 Declared the channels.")

    def build_side(self, router: APIRouter) -> Side:
        path_inner_memo = os.path.join("memo", f"{self.sidename}_inner_memo")
        default_inner_memo = InnerMemo(
            FilesystemMemoBroker(path_inner_memo),
            # ShelveMemoBroker(name_inner_memo),
        )
        side_inner_memo = (
            default_inner_memo
            if isinstance(self.inner_memo, NoneInnerMemo)
            else self.inner_memo
        )

        if self.sidename == "appearance":
            return AppearanceSide(
                router,
                configure=self.configure,
                savant_router=self.savant_router,
                context_memo=self.context_memo,
                inner_memo=side_inner_memo,
            )

        if self.sidename == "brain":
            return BrainSide(
                router,
                savant_router=self.savant_router,
                acts=self.configure.acts,
                runs=self.brain_runs,
            )

        if self.sidename == "keeper":
            return KeeperSide(
                router,
                savant_router=self.savant_router,
                acts=self.configure.acts,
                inner_memo=side_inner_memo,
            )

        raise Exception(f"Undeclared side `{self.sidename}`.")

    # properties

    language: str = Field(
        ...,
        title="Language",
        description="The language of aide. Show info about the aide in that language.",
    )

    configure: Configure = Field(
        ...,
        title="Configure",
        description="The configuration of aide.",
    )

    name: str = Field(
        ...,
        title="Name",
        description="The name of aide.",
    )

    @property
    def hid(self):
        return self.configure.hid

    sidename: str = Field(
        ...,
        title="Sidename",
        description="The sidename of aide. Lowercase.",
    )

    tags: List[str] = Field(
        default=[],
        title="Tags",
        description="The tags for aide.",
    )

    side: Side = Field(
        ...,
        title="Side",
        description="The side of aide. Set by class name.",
    )

    brain_runs: List[Callable] = Field(
        default=[],
        title="Brain Runs",
        description="The runs for Brain server. Each runs should be defined into `configure.json` with same name.",
    )

    savant_router: SavantRouter = Field(
        ...,
        title="Savant Router",
        description="The router to Savant server.",
    )

    # Check the declared routes.
    def _check_routes(self):
        for route in self.routes:
            if isinstance(route, routing.APIRoute) and not skip_check_route(route):
                logger.info(f"Checking {route}...")

                if route.path.lower() != route.path:
                    raise Exception("The route API should be declared in lowercase.")

                tpath = route.path[1:].replace("_", "-").replace("/", "-").lower()
                if tpath != route.name.replace("_", "-"):
                    raise Exception(
                        "The route API should be declared with `-` instead of `_`"
                        " and it should have the same names for path and name."
                        f" Have: `{tpath}` != `{route.name}`."
                    )

                logger.info(f"Checked route `{route.path}`. It's OK.")

    # Simplify operation IDs into the routes.
    def _use_route_names_as_operation_ids(self) -> List[routing.APIRoute]:
        r = []
        for route in self.routes:
            if isinstance(route, routing.APIRoute) and not skip_check_route(route):
                route.operation_id = route.name
                r.append(route)

        return r

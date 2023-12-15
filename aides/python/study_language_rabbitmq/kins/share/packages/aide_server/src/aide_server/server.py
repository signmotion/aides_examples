from fastapi import APIRouter, FastAPI, routing
import logging
from pydantic import Field
from typing import Callable, List

from .configure import Configure
from .context_memo import ContextMemo, NoneContextMemo
from .helpers import unwrapMultilangTextList, skip_check_route
from .inner_memo import InnerMemo, NoneInnerMemo
from .log import logger
from .routers import about, context
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
        configure: Configure,
        brain_runs: List[Callable] = [],
        inner_memo: InnerMemo = NoneInnerMemo(),
        context_memo: ContextMemo = NoneContextMemo(),
        language: str = "en",
        debug_level: int = logging.INFO,
    ):
        logging.basicConfig(level=debug_level)

        tags = unwrapMultilangTextList(configure.tags, language=language)
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
            configure.savantConnector,
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
        self.include_routers()

    def register_side(self):
        logger.info(f"🏳️‍🌈 Initializing the side `{self.sidename}`...")

        # adding runs as external routers
        router = APIRouter()

        # TODO Wrap to factory.
        if self.sidename == "appearance":
            if isinstance(self.context_memo, NoneContextMemo):
                raise Exception("The Appearance should have a context memo.")

            # add context routers
            self.include_router(context.router(self.context_memo))
            logger.info("🍁 Added the router for `Context`.")

            self.side = AppearanceSide(
                router,
                savant_router=self.savant_router,
                acts=self.configure.acts,
                inner_memo=self.inner_memo,
            )
        elif self.sidename == "brain":
            assert bool(self.brain_runs)
            assert len(self.brain_runs) == len(self.configure.acts)
            self.side = BrainSide(
                router,
                savant_router=self.savant_router,
                acts=self.configure.acts,
                runs=self.brain_runs,
            )
        elif self.sidename == "keeper":
            self.side = KeeperSide(
                router,
                savant_router=self.savant_router,
                acts=self.configure.acts,
                inner_memo=self.inner_memo,
            )

        logger.info(f"🏳️‍🌈 Initialized the side `{self.sidename}`.")

        self.include_router(router)
        logger.info(f"🍁 Included the router to the side `{self.sidename}`.")

        # !) call this functions after adding all routers
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
                queue=self.savant_router.logQueue(),
                exchange=self.savant_router.exchange(),
                timeout=5,
            )

        @self.savant_router.broker.subscriber(
            self.savant_router.logQueue(),
            self.savant_router.exchange(),
        )
        async def check_connection_to_savant(message: str):
            logger.info(
                "😎 Connection to Savant"
                f" from `{self.sidename}` `{self.hid}` confirmed."
                # f' Message received: "{message[:24]}...{message[-12:]}"'
            )

        logger.info("🌱 Declared the channels.")

    def include_routers(self):
        logger.info("🍁 Adding the routers...")

        # add about routers
        self.include_router(
            about.router(
                name=self.name,
                hid=self.hid,
                sidename=self.sidename,
                path_to_face=self.configure.path_to_face,
            )
        )
        logger.info("🍁 Added the router for `About`.")

        logger.info("🍁 Added the routers.")

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

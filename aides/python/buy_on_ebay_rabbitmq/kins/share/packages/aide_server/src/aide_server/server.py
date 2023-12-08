import logging
import time
from fastapi import APIRouter, FastAPI, routing
from faststream.rabbit import (
    RabbitBroker,
    ExchangeType,
    RabbitExchange,
    RabbitQueue,
    fastapi,
)

from typing import List, Optional
from pydantic import Field

from .routers import about, context
from .configure import Configure
from .memo import Memo, NoneMemo


logger = logging.getLogger("uvicorn.error")


class AideServer(FastAPI):
    """
    Aide Server.
    """

    def __init__(
        self,
        *,
        language: str,
        configure: Configure,
        memo: Memo = NoneMemo(),
        external_routers: List[APIRouter] = [],
        debug_level: int = logging.INFO,
    ):
        logging.basicConfig(level=debug_level)

        tags = [tag.get(language) or "" for tag in configure.tags if language in tag]
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

        name = configure.name.get(language) or "AideServer"
        savantRouter = fastapi.RabbitRouter(configure.savantConnector)

        super().__init__(
            title=name,
            summary=configure.summary.get(self.language),
            description=configure.description.get(self.language) or "",
            version=configure.version,
            openapi_tags=openapi_tags,
            lifespan=savantRouter.lifespan_context,
        )

        self.language = language
        self.name = name
        self.tags = tags
        self.configure = configure
        self.memo = memo
        self.part = type(self).__name__
        self.savantRouter = savantRouter

        self.include_routers(external_routers)
        self.declare_channels()

    def include_routers(self, external_routers: List[APIRouter]):
        # add about routers
        self.include_router(
            about.router(
                name=self.name,
                nickname=self.nickname,
                part=self.part,
                path_to_face=self.configure.path_to_face,
            )
        )

        # add context routers
        self.include_router(context.router(self.memo))

        # add external routers
        for external_router in external_routers:
            self.include_router(external_router)

        # !) call this functions after adding all routers
        self._check_routes()
        self._use_route_names_as_operation_ids()

    def declare_channels(self):
        @self.savantRouter.after_startup
        async def app_started(app: AideServer):
            await self._declare_exchange()
            await self._declare_service_queues()
            await self._declare_routes_queues()

            message = (
                f"`{self.part}` `{app.title}` `{self.nickname}`"
                " powered by FastStream & FastAPI"
                " started."
            )
            logger.info(message)

            logger.info(f"Testing connection to Savant `{self.savant.url}`...")
            await self.savant.publish(
                message,
                exchange=self.exchange(),
                queue=self.logQueue(),
                timeout=5,
            )

        @self.savant.subscriber(self.logQueue(), self.exchange())
        async def test_connected_to_savant(message: str):
            logger.info(
                "Connection to Savant"
                f" from `{self.part}` `{self.nickname}` confirmed."
                # f' Message received: "{message[:24]}...{message[-12:]}"'
            )

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
    def nickname(self):
        return self.configure.nickname

    tags: List[str] = Field(
        default=[],
        title="Tags",
        description="The tags for aide.",
    )

    part: str = Field(
        ...,
        title="Part",
        description="The name for part of aide. Set by class name.",
    )

    memo: Memo = Field(
        default=NoneMemo(),
        title="Memo",
        description="The memory of aide. Keep a generic context.",
    )

    savantRouter: fastapi.RabbitRouter = Field(
        ...,
        title="Savant Router",
        description="The router to Savant server.",
    )

    @property
    def savantConnector(self):
        return self.configure.savantConnector

    @property
    def savant(self) -> RabbitBroker:
        return self.savantRouter.broker

    def exchange(self):
        return RabbitExchange("aide", auto_delete=True, type=ExchangeType.TOPIC)

    def queryQueue(
        self,
        router: Optional[APIRouter] = None,
        route_name: str = "",
    ):
        return self._queueRouter(
            "query",
            include_part=False,
            router=router,
            route_name=route_name,
        )

    def progressQueue(
        self,
        router: Optional[APIRouter] = None,
        route_name: str = "",
    ):
        return self._queueRouter(
            "progress",
            include_part=False,
            router=router,
            route_name=route_name,
        )

    def resultQueue(
        self,
        router: Optional[APIRouter] = None,
        route_name: str = "",
    ):
        return self._queueRouter(
            "result",
            include_part=False,
            router=router,
            route_name=route_name,
        )

    def requestProgressQueue(self):
        return self._requestActQueue("progress")

    def requestResultQueue(self):
        return self._requestActQueue("result")

    def responseProgressQueue(self):
        return self._responseActQueue("progress")

    def responseResultQueue(self):
        return self._responseActQueue("result")

    def logQueue(self, router: Optional[APIRouter] = None, route_name: str = ""):
        return self._queueRouter(
            "log",
            include_part=True,
            router=router or self.savantRouter,
            route_name=route_name,
        )

    def _queueRouter(
        self,
        name_queue: str,
        include_part: bool,
        router: Optional[APIRouter] = None,
        route_name: str = "",
    ):
        act = route_name or (router.name if hasattr(router, "name") else type(router).__name__) or ""  # type: ignore
        return self._queueAct(name_queue, act=act, include_part=include_part)

    def _requestActQueue(self, act: str):
        return self._queueAct("request", act=act, include_part=False)

    def _responseActQueue(self, act: str):
        return self._queueAct("response", act=act, include_part=False)

    def _queueAct(
        self,
        name_queue: str,
        act: str,
        include_part: bool,
    ):
        keys = [
            act,
            self.part.lower() if include_part else "*",
            self.nickname,
        ]

        return RabbitQueue(
            name_queue,
            auto_delete=True,
            routing_key=".".join(keys),
        )

    async def _declare_exchange(self):
        declare = self.savant.declare_exchange
        ex = self.exchange()
        await declare(ex)
        logger.info(f"\tCreated exchange `{ex.name}` with type\t{ex.type.upper}.")

    async def _declare_queue(self, queue: RabbitQueue):
        await self.savant.declare_queue(queue)
        logger.info(f"\tCreated queue `{queue.name}` with key\t{queue.routing_key}.")

    async def _declare_service_queues(self):
        logger.info(f"Declaring service queues...")

        await self._declare_queue(self.requestProgressQueue())
        await self._declare_queue(self.requestResultQueue())
        await self._declare_queue(self.responseProgressQueue())
        await self._declare_queue(self.responseResultQueue())
        await self._declare_queue(self.logQueue())

        logger.info(f"Declared service queues.")

    async def _declare_routes_queues(self):
        # TODO optimize We don't need the queues for all routes.
        for route in self.routes:
            if isinstance(route, routing.APIRoute) and not self._skip_check_route(
                route
            ):
                logger.info(f"Declaring queues for route `{route.name}`...")

                await self._declare_queue(self.queryQueue(route_name=route.name))
                await self._declare_queue(self.progressQueue(route_name=route.name))
                await self._declare_queue(self.resultQueue(route_name=route.name))
                time.sleep(0.2)

                logger.info(f"Declared queues for route `{route.path}`.")

    # Check the declared routes.
    def _check_routes(self):
        for route in self.routes:
            if isinstance(route, routing.APIRoute) and not self._skip_check_route(
                route
            ):
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

    def _skip_check_route(self, route: routing.APIRoute) -> bool:
        return (
            route.name == "root"
            or "asyncapi" in route.path
            or "/context" in route.path
            or "{" in route.path
        )

    # Simplify operation IDs into the routes.
    def _use_route_names_as_operation_ids(self) -> List[routing.APIRoute]:
        r = []
        for route in self.routes:
            if isinstance(route, routing.APIRoute) and not self._skip_check_route(
                route
            ):
                route.operation_id = route.name
                r.append(route)

        return r

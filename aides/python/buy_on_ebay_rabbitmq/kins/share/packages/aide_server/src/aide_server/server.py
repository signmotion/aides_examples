import time
from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse
from faststream.rabbit import (
    RabbitBroker,
    ExchangeType,
    RabbitExchange,
    RabbitQueue,
    fastapi,
)

from typing import List, Optional
from fastapi import routing
from pydantic import Field

from .routers import about, context
from .configure import Configure
from .memo import Memo, NoneMemo


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
    ):
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
                f"\nFastStream powered by FastAPI server `{app.title}`"
                f" defined as `{self.part}`"
                f" with nickname `{self.nickname}`"
                " started.\n"
            )
            print(message)

            await self.broker.publish(
                message.strip(),
                exchange=self.exchange(),
                queue=self.logQueue(),
                timeout=5,
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
    def broker(self) -> RabbitBroker:
        return self.savantRouter.broker

    def exchange(self):
        return RabbitExchange("aide", auto_delete=True, type=ExchangeType.HEADERS)

    def queryQueue(
        self,
        router: Optional[APIRouter] = None,
        route_name: str = "",
    ):
        return self._queueRouter("query", router=router, route_name=route_name)

    def progressQueue(
        self,
        router: Optional[APIRouter] = None,
        route_name: str = "",
    ):
        return self._queueRouter("progress", router=router, route_name=route_name)

    def resultQueue(
        self,
        router: Optional[APIRouter] = None,
        route_name: str = "",
    ):
        return self._queueRouter("result", router=router, route_name=route_name)

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
            router=router or self.savantRouter,
            route_name=route_name,
        )

    def _queueRouter(
        self,
        name_queue: str,
        router: Optional[APIRouter] = None,
        route_name: str = "",
    ):
        act = route_name or (router.name if hasattr(router, "name") else type(router).__name__) or ""  # type: ignore
        return self._queueAct(name_queue, act=act)

    def _requestActQueue(self, act: str):
        return self._queueAct("request", act=act)

    def _responseActQueue(self, act: str):
        return self._queueAct("response", act=act)

    def _queueAct(self, name_queue: str, act: str):
        return RabbitQueue(
            name_queue,
            auto_delete=True,
            bind_arguments={
                "act": act,
                "nickname": self.nickname,
            },
        )

    async def _declare_exchange(self):
        declare = self.broker.declare_exchange
        ex = self.exchange()
        await declare(ex)
        print(f"\tCreated exchange `{ex.name}` with\t{ex.type}.")

    async def _declare_queue(self, queue: RabbitQueue):
        await self.broker.declare_queue(queue)
        print(f"\tCreated queue `{queue.name}` with\t{queue.bind_arguments}.")

    async def _declare_service_queues(self):
        print(f"\nDeclaring service queues...")

        await self._declare_queue(self.requestProgressQueue())
        await self._declare_queue(self.requestResultQueue())
        await self._declare_queue(self.responseProgressQueue())
        await self._declare_queue(self.responseResultQueue())
        await self._declare_queue(self.logQueue())

        print(f"Declared service queues.")

    async def _declare_routes_queues(self):
        # TODO optimize We don't need the queues for all routes.
        for route in self.routes:
            if isinstance(route, routing.APIRoute) and not self._skip_check_route(
                route
            ):
                print(f"\nDeclaring queues for route `{route.name}`...")

                await self._declare_queue(self.queryQueue(route_name=route.name))
                await self._declare_queue(self.progressQueue(route_name=route.name))
                await self._declare_queue(self.resultQueue(route_name=route.name))
                time.sleep(0.2)

                print(f"Declared queues for route `{route.path}`.")

    # Check the declared routes.
    def _check_routes(self):
        for route in self.routes:
            if isinstance(route, routing.APIRoute) and not self._skip_check_route(
                route
            ):
                print(f"\nChecking {route}...")

                if route.path.lower() != route.path:
                    raise Exception("The route API should be declared in lowercase.")

                tpath = route.path[1:].replace("_", "-").replace("/", "-").lower()
                if tpath != route.name.replace("_", "-"):
                    raise Exception(
                        "The route API should be declared with `-` instead of `_`"
                        " and it should have the same names for path and name."
                        f" Have: `{tpath}` != `{route.name}`."
                    )

                print(f"Checked route `{route.path}`. It's OK.")

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

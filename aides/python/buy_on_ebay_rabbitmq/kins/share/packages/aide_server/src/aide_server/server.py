import json
import time
from fastapi import APIRouter, Body, Depends, FastAPI
from fastapi.responses import FileResponse
from faststream.rabbit import (
    RabbitBroker,
    ExchangeType,
    RabbitExchange,
    RabbitQueue,
    fastapi,
)

from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

from fastapi import routing
from fastapi.datastructures import Default

from fastapi.params import Depends
from fastapi.utils import generate_unique_id
from pydantic import BaseModel, Field
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute

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
        self.external_routers = external_routers
        self.part = type(self).__name__
        self.savantRouter = savantRouter

        self.include_routers()
        self.declare_channels()

    def include_routers(self):
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
        for external_router in self.external_routers:
            self.include_router(external_router)

        # !) call this functions after adding all routers
        _check_routes(self)
        _use_route_names_as_operation_ids(self)

    def declare_channels(self):
        @self.savantRouter.after_startup
        async def app_started(app: AideServer):
            await _declare_exchange(self)
            await _declare_service_queues(self)
            await _declare_routes_queues(self)

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
        description="The memory of aide.",
    )

    savantRouter: fastapi.RabbitRouter = Field(
        ...,
        title="Savant Router",
        description="The router to Savant server.",
    )

    external_routers: List[APIRouter] = Field(
        default=[],
        title="External Routers",
        description="The declared routers (set of endpoints) into aide.",
    )

    @property
    def savantConnector(self):
        return self.configure.savantConnector

    @property
    def broker(self):
        return self.savantRouter.broker  # type: ignore

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
        return _queueRouter(
            "log",
            router=router or self.savantRouter,
            route_name=route_name,
            nickname_aide=self.nickname,
        )

    def _queueRouter(
        self,
        name_queue: str,
        router: Optional[APIRouter] = None,
        route_name: str = "",
    ):
        return _queueRouter(
            name_queue,
            router=router,
            route_name=route_name,
            nickname_aide=self.nickname,
        )

    def _requestActQueue(self, act: str):
        return _queueAct("request", act=act, nickname_aide=self.nickname)

    def _responseActQueue(self, act: str):
        return _queueAct("response", act=act, nickname_aide=self.nickname)

    # Keep a generic context.
    memo: Memo = NoneMemo()


def _queueRouter(
    name_queue: str,
    nickname_aide: str,
    router: Optional[APIRouter] = None,
    route_name: str = "",
):
    act = route_name or (router.name if hasattr(router, "name") else type(router).__name__) or ""  # type: ignore
    return _queueAct(
        name_queue,
        act=act,
        nickname_aide=nickname_aide,
    )


def _queueAct(name_queue: str, act: str, nickname_aide: str):
    return RabbitQueue(
        name_queue,
        auto_delete=True,
        bind_arguments={
            "act": act,
            "nickname": nickname_aide,
        },
    )


async def _declare_exchange(server: AideServer):
    declare = server.broker.declare_exchange
    await declare(server.exchange())


async def _declare_queue(server: AideServer, queue: RabbitQueue):
    await server.broker.declare_queue(queue)
    print(f"\tCreated queue `{queue.name}` with\t{queue.bind_arguments}.")


async def _declare_service_queues(server: AideServer):
    print(f"\nDeclaring service queues...")

    await _declare_queue(server, server.requestProgressQueue())
    await _declare_queue(server, server.requestResultQueue())
    await _declare_queue(server, server.responseProgressQueue())
    await _declare_queue(server, server.responseResultQueue())
    await _declare_queue(server, server.logQueue())

    print(f"Declared service queues.")


async def _declare_routes_queues(server: AideServer):
    # TODO optimize We don't need the queues for all routes.
    for route in server.routes:
        if isinstance(route, routing.APIRoute) and not _skip_check_route(route):
            print(f"\nDeclaring queues for route `{route.name}`...")

            await _declare_queue(server, server.queryQueue(route_name=route.name))
            await _declare_queue(server, server.progressQueue(route_name=route.name))
            await _declare_queue(server, server.resultQueue(route_name=route.name))
            time.sleep(0.2)

            print(f"Declared queues for route `{route.path}`.")


# Check the declared routes.
def _check_routes(server: AideServer):
    for route in server.routes:
        if isinstance(route, routing.APIRoute) and not _skip_check_route(route):
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

            print(f"Checked route `{route.name}`. It's OK.")


def _skip_check_route(route: routing.APIRoute) -> bool:
    return (
        route.name == "root"
        or "asyncapi" in route.path
        or "/context" in route.path
        or "{" in route.path
    )


# Simplify operation IDs into the routes.
def _use_route_names_as_operation_ids(server: FastAPI) -> List[routing.APIRoute]:
    r = []
    for route in server.routes:
        if isinstance(route, routing.APIRoute) and not _skip_check_route(route):
            route.operation_id = route.name
            r.append(route)

    return r

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


class AideServer:
    """
    Aide Server.
    """

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self,
        *,
        language: str,
        configure: Configure,
        memo: Memo = NoneMemo(),
        external_routers: List[APIRouter] = [],
    ):
        self.language = language
        self.configure = configure
        self.memo = memo
        self.external_routers = external_routers
        self.part = type(self).__name__
        self.savantRouter = fastapi.RabbitRouter(self.savantConnector)

    # properties

    # @property
    async def fastapi_app(self):
        openapi_tags = []
        tags = self.tags("en")
        if bool(tags):
            openapi_tags.append(
                {
                    "name": "tags",
                    "value": tags,
                }
            )

        if self.configure.characteristic:
            openapi_tags.append(
                {
                    "name": "characteristic",
                    "value": self.configure.characteristic,
                }
            )

        app = FastAPI(
            title=self.name,
            summary=self.configure.summary.get(self.language),
            description=self.configure.description.get(self.language) or "",
            version=self.configure.version,
            openapi_tags=openapi_tags,
            lifespan=self.savantRouter.lifespan_context,
        )

        # add about routers
        app.include_router(
            about.router(
                name=self.name,
                nickname=self.nickname,
                part=self.part,
                path_to_face=self.configure.path_to_face,
            )
        )

        # add context routers
        app.include_router(context.router(self.memo))

        # add external routers
        for external_router in self.external_routers:
            app.include_router(external_router)

        # !) call this functions after adding all routers
        _check_routes(app)
        rs = _use_route_names_as_operation_ids(app)

        await _declare_exchange(self)
        await _declare_service_queues(self)
        await _declare_routes_queues(self, routes=rs)

        @self.savantRouter.after_startup
        async def app_started(app: FastAPI):
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

        return app

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

    @property
    def name(self):
        return self.configure.name.get(self.language) or ""

    @property
    def nickname(self):
        return self.configure.nickname

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

    def tags(self, language: str):
        return [tag.get(language) for tag in self.configure.tags if language in tag]

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


async def _declare_service_queues(server: AideServer):
    declare = server.broker.declare_queue

    await declare(server.requestProgressQueue())
    await declare(server.requestResultQueue())
    await declare(server.responseProgressQueue())
    await declare(server.responseResultQueue())
    await declare(server.logQueue())


async def _declare_routes_queues(server: AideServer, routes: List[routing.APIRoute]):
    declare = server.broker.declare_queue

    for route in routes:
        await declare(server.queryQueue(route_name=route.name))
        await declare(server.progressQueue(route_name=route.name))
        await declare(server.resultQueue(route_name=route.name))
        print(f"Declared queues for route `{route.name}`.")
        time.sleep(0.2)


# Check the declared routes.
def _check_routes(server: FastAPI):
    for route in server.routes:
        if isinstance(route, routing.APIRoute):
            print(f"{route}")

            if route.path.lower() != route.path:
                raise Exception("The route API should be declared in lowercase.")

            if not _skip_check_route(route):
                tpath = route.path[1:].replace("_", "-").replace("/", "-").lower()
                if tpath != route.name.replace("_", "-"):
                    raise Exception(
                        "The route API should be declared with `-` instead of `_`"
                        " and it should have the same names for path and name."
                        f" Have: `{tpath}` != `{route.name}`."
                    )


def _skip_check_route(route: routing.APIRoute):
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
        if isinstance(route, routing.APIRoute):
            print(f"{route.operation_id} -> {route.name}")
            route.operation_id = route.name
            r.append(route)

    return r

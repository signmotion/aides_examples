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
from pydantic import Field
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute

from .configure import Configure

from .memo import Memo, NoneMemo


class AideServer(FastAPI):
    """
    Aide Server.
    """

    def __init__(
        self,
        *,
        # own
        configure: Configure,
        memo: Memo = NoneMemo(),
        external_routers: List[APIRouter] = [],
        # from FastAPI
        debug: bool = False,
        routes: Optional[List[BaseRoute]] = None,
        title: str = "AideServer",
        summary: Optional[str] = None,
        description: str = "",
        version: str = "0.1.0",
        openapi_url: Optional[str] = "/openapi.json",
        openapi_tags: List[Dict[str, Any]] = [],
        servers: Optional[List[Dict[str, Union[str, Any]]]] = None,
        dependencies: Optional[Sequence[Depends]] = None,
        default_response_class: Type[Response] = Default(JSONResponse),
        redirect_slashes: bool = True,
        docs_url: Optional[str] = "/docs",
        redoc_url: Optional[str] = "/redoc",
        swagger_ui_oauth2_redirect_url: Optional[str] = "/docs/oauth2-redirect",
        swagger_ui_init_oauth: Optional[Dict[str, Any]] = None,
        middleware: Optional[Sequence[Middleware]] = None,
        exception_handlers: Optional[
            Dict[
                Union[int, Type[Exception]],
                Callable[[Request, Any], Coroutine[Any, Any, Response]],
            ]
        ] = None,
        on_startup: Optional[Sequence[Callable[[], Any]]] = None,
        on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
        # lifespan: Optional[Lifespan[AppType]] = None,
        terms_of_service: Optional[str] = None,
        contact: Optional[Dict[str, Union[str, Any]]] = None,
        license_info: Optional[Dict[str, Union[str, Any]]] = None,
        openapi_prefix: str = "",
        root_path: str = "",
        root_path_in_servers: bool = True,
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        callbacks: Optional[List[BaseRoute]] = None,
        webhooks: Optional[routing.APIRouter] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        swagger_ui_parameters: Optional[Dict[str, Any]] = None,
        generate_unique_id_function: Callable[[routing.APIRoute], str] = Default(
            generate_unique_id
        ),
        separate_input_output_schemas: bool = True,
        **extra: Any,
    ):
        self.configure = configure
        self.memo = memo

        savantRouter = fastapi.RabbitRouter(self.savantConnector)

        additional_tags = []
        tags = self.tags("en")
        if bool(tags):
            additional_tags.append(
                {
                    "name": "tags",
                    "value": tags,
                }
            )

        if self.configure.characteristic:
            additional_tags.append(
                {
                    "name": "characteristic",
                    "value": self.configure.characteristic,
                }
            )

        super().__init__(
            debug=debug,
            routes=routes,
            title=title,
            summary=summary,
            description=description,
            version=version,
            openapi_url=openapi_url,
            openapi_tags=additional_tags + openapi_tags,
            servers=servers,
            dependencies=dependencies,
            default_response_class=default_response_class,
            redirect_slashes=redirect_slashes,
            docs_url=docs_url,
            redoc_url=redoc_url,
            swagger_ui_oauth2_redirect_url=swagger_ui_oauth2_redirect_url,
            swagger_ui_init_oauth=swagger_ui_init_oauth,
            middleware=middleware,
            exception_handlers=exception_handlers,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            lifespan=savantRouter.lifespan_context,
            terms_of_service=terms_of_service,
            contact=contact,
            license_info=license_info,
            openapi_prefix=openapi_prefix,
            root_path=root_path,
            root_path_in_servers=root_path_in_servers,
            responses=responses,
            callbacks=callbacks,
            webhooks=webhooks,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            swagger_ui_parameters=swagger_ui_parameters,
            generate_unique_id_function=generate_unique_id_function,
            separate_input_output_schemas=separate_input_output_schemas,
            extra=extra,
        )

        self.part = type(self).__name__

        _init_about_router(self)
        _init_context_router(self)
        _init_external_routers(self, external_routers=external_routers)

        # !) call this functions after adding all routers
        _check_routes(self)
        rs = _use_route_names_as_operation_ids(self)

        @savantRouter.after_startup
        async def start(self):
            self.router = savantRouter

            await _declare_exchange(self)
            await _declare_service_queues(self)
            await _declare_routes_queues(self, routes=rs)

            message = (
                f"\nFastStream powered by FastAPI server `{self.title}`"
                f" defined as `{self.part}`"
                f" with nickname `{self.nickname}`"
                " started.\n"
            )
            print(message)

            await self.broker().publish(
                message.strip(),
                exchange=self.exchange(),
                queue=self.logQueue(),
                timeout=5,
            )

    # properties

    configure: Configure = Field(
        ...,
        title="Configure",
        description="The configuration of aide.",
    )

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

    @property
    def savantConnector(self):
        return self.configure.savantConnector

    def tags(self, language: str):
        return [tag.get(language) for tag in self.configure.tags if language in tag]

    def broker(self):
        return self.router.broker  # type: ignore

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
            router=router or self.router,
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


def _init_about_router(server: AideServer):
    router = APIRouter()

    @router.get("/")
    def root():
        return {
            "title": server.title,
            "nickname": server.nickname,
            "part": server.part,
        }

    @router.get("/face", include_in_schema=False)
    def face():
        return FileResponse("app/data/face.webp")

    server.include_router(router)


def _init_context_router(server: AideServer):
    router = APIRouter()

    @router.get("/schema")
    def schema():
        return json.loads(server.memo.context.schema_json())

    @router.get("/get-context")
    def get_context():
        return server.memo.context

    @router.get("/get-context-value/{hid}")
    def get_context_value(hid: str):
        return getattr(server.memo.context, hid)

    # See [schema].
    @router.put("/set-context-value")
    def set_context_value(
        hid: str = Body(
            embed=True,
            title="HID",
            description="ID for human perception.",
        ),
        value: str = Body(
            embed=True,
            title="Value",
            description="Value for set by HID.",
        ),
    ):
        setattr(server.memo.context, hid, value)
        return True

    server.include_router(router)


def _init_external_routers(server: AideServer, external_routers: List[APIRouter]):
    for router in external_routers:
        server.include_router(router)


async def _declare_exchange(server: AideServer):
    declare = server.broker().declare_exchange
    await declare(server.exchange())


async def _declare_service_queues(server: AideServer):
    declare = server.broker().declare_queue

    await declare(server.requestProgressQueue())
    await declare(server.requestResultQueue())
    await declare(server.responseProgressQueue())
    await declare(server.responseResultQueue())
    await declare(server.logQueue())


async def _declare_routes_queues(server: AideServer, routes: List[routing.APIRoute]):
    declare = server.broker().declare_queue

    for route in routes:
        await declare(server.queryQueue(route_name=route.name))
        await declare(server.progressQueue(route_name=route.name))
        await declare(server.resultQueue(route_name=route.name))
        print(f"Declared queues for route `{route.name}`.")
        time.sleep(0.2)


# Check the declared routes.
def _check_routes(server: AideServer):
    for route in server.routes:
        if isinstance(route, routing.APIRoute):
            print(f"{route}")

            if route.path.lower() != route.path:
                raise Exception("The route API should be declared in lowercase.")

            if (
                route.name != "root"
                and route.path != "/context"
                and "{" not in route.path
            ):
                tpath = route.path[1:].replace("_", "-").replace("/", "-").lower()
                if tpath != route.name.replace("_", "-"):
                    raise Exception(
                        "The route API should be declared with `-` instead of `_`"
                        " and it should have the same names for path and name."
                        f" Have: `{tpath}` != `{route.name}`."
                    )


# Simplify operation IDs into the routes.
def _use_route_names_as_operation_ids(server: AideServer) -> List[routing.APIRoute]:
    r = []
    for route in server.routes:
        if isinstance(route, routing.APIRoute):
            print(f"{route.operation_id} -> {route.name}")
            route.operation_id = route.name
            r.append(route)

    return r

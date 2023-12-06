import json
from fastapi import APIRouter, Body, Depends, FastAPI
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
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute
from starlette.types import Lifespan

from .memo import Memo


defaultSavantConnector = "amqp://guest:guest@localhost:5672/"


class AideServer(FastAPI):
    def __init__(
        self,
        *,
        # own
        nickname: str = "",
        tags: Optional[List[str]] = None,
        characteristic: Optional[Dict[str, Any]] = None,
        external_routers: Optional[List[APIRouter]] = [],
        memo: Memo,
        savantConnector: str = defaultSavantConnector,
        # from FastAPI
        debug: bool = False,
        routes: Optional[List[BaseRoute]] = None,
        title: str = "AideServer",
        summary: Optional[str] = None,
        description: str = "",
        version: str = "0.1.0",
        openapi_url: Optional[str] = "/openapi.json",
        openapi_tags: Optional[List[Dict[str, Any]]] = [],
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
        self.nickname = nickname  # type: ignore
        self.memo = memo  # type: ignore

        router = fastapi.RabbitRouter(savantConnector)

        additional_tags = []
        if characteristic:
            additional_tags = [
                {
                    "name": "tags",
                    "value": tags,
                },
                {
                    "name": "characteristic",
                    "value": characteristic,
                },
            ]

        super().__init__(
            debug=debug,
            routes=routes,
            title=title,
            summary=summary,
            description=description,
            version=version,
            openapi_url=openapi_url,
            openapi_tags=additional_tags + openapi_tags,  # type: ignore
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
            lifespan=router.lifespan_context,
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

        _init_rabbit_router(self, router)

        _init_about_routers(self)
        _init_context_routers(self)
        _init_external_routers(self, external_routers=external_routers)

        # !) call this functions after adding all routers
        _check_routes(self)  # type: ignore
        _use_route_names_as_operation_ids(self)

    def broker(self):
        return self.router.broker  # type: ignore

    # def exchange(self):
    #     return RabbitExchange("aide", auto_delete=True, type=ExchangeType.HEADERS)

    # def queryQueue(self, router: APIRouter):
    #     return self._queueRouter("query", router=router)

    # def progressQueue(self, router: APIRouter):
    #     return self._queueRouter("progress", router=router)

    # def resultQueue(self, router: APIRouter):
    #     return self._queueRouter("result", router=router)

    # def requestProgressQueue(self):
    #     return self._requestActQueue("progress")

    # def requestResultQueue(self):
    #     return self._requestActQueue("result")

    # def responseProgressQueue(self):
    #     return self._responseActQueue("progress")

    # def responseResultQueue(self):
    #     return self._responseActQueue("result")

    # def logQueue(self, router: APIRouter):
    #     return _queueRouter("log", router=router, nickname_aide=self.nickname)

    def _queueRouter(self, name_queue: str, router: APIRouter):
        return _queueRouter(name_queue, router=router, nickname_aide=self.nickname)

    def _requestActQueue(self, act: str):
        return _queueAct("request", act=act, nickname_aide=self.nickname)

    def _responseActQueue(self, act: str):
        return _queueAct("response", act=act, nickname_aide=self.nickname)

    # Keep a generic context.
    memo: Union[Memo, None] = None


def _queueRouter(name_queue: str, router: APIRouter, nickname_aide: str):
    return _queueAct(
        name_queue,
        act=router.name if hasattr(router, "name") else type(router).__name__,  # type: ignore
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


def _init_rabbit_router(server: AideServer, router: fastapi.RabbitRouter):
    @router.after_startup
    async def start(server):
        server.router = router

        server.exchange = RabbitExchange(
            "aide",
            auto_delete=True,
            type=ExchangeType.HEADERS,
        )
        await server.broker().declare_exchange(server.exchange)

        server.logQueue = _queueRouter(
            "log",
            router=router,
            nickname_aide=server.nickname,
        )
        await server.broker().declare_queue(server.logQueue)

        message = (
            f"\nFastStream powered by FastAPI server `{server.title}`"
            f" with nickname `{server.nickname}`"
            " started.\n"
        )
        print(message)

        await server.broker().publish(
            message.strip(),
            exchange=server.exchange,
            queue=server.logQueue,
            timeout=5,
        )


def _init_about_routers(server: AideServer):
    router = APIRouter()

    @router.get("/")
    def root():
        return {
            "title": server.title,
            "nickname": server.nickname,
        }

    server.include_router(router)


def _init_context_routers(server: AideServer):
    router = APIRouter()

    @router.get("/context")
    def context():
        return server.memo.context  # type: ignore

    @router.get("/schema")
    def schema():
        return json.loads(server.memo.context.schema_json())  # type: ignore

    @router.get("/context/{hid}")
    def value(hid: str):
        return getattr(server.memo.context, hid)  # type: ignore

    # See [schema].
    @router.put("/context/{hid}/{value}")
    def put_inline_hid_value(hid: str, value: str):
        setattr(server.memo.context, hid, value)  # type: ignore
        return True

    # See [schema].
    @router.put("/context/{hid}")
    def put_inline_hid_json_value(
        hid: str,
        value: str = Body(embed=True),
    ):
        setattr(server.memo.context, hid, value)  # type: ignore
        return True

    # See [schema].
    @router.put("/context")
    def put_json_hid_value(
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
        setattr(server.memo.context, hid, value)  # type: ignore
        return True

    server.include_router(router)


def _init_external_routers(server, external_routers):
    print(external_routers)
    for router in external_routers:
        server.include_router(router)


# Check the declared routes.
def _check_routes(server: AideServer):
    for route in server.routes:
        if isinstance(route, routing.APIRoute):
            print(f"\n{route}")

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
def _use_route_names_as_operation_ids(app: FastAPI):
    for route in app.routes:
        if isinstance(route, routing.APIRoute):
            print(f"{route.operation_id} -> {route.name}")
            route.operation_id = route.name

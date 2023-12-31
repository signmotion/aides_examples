import json
from fastapi import APIRouter, Body, FastAPI
from fastapi.applications import AppType

from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
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


class AideServer(FastAPI):
    def __init__(
        self: AppType,
        *,
        # own
        tags: Optional[List[str]] = None,
        characteristic: Optional[Dict[str, Any]] = None,
        external_routers: Optional[List[APIRouter]] = [],
        memo: Memo,
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
        lifespan: Optional[Lifespan[AppType]] = None,
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
        self.memo = memo

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
            lifespan=lifespan,
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

        _init_context_routers(self)
        _init_external_routers(self, external_routers=external_routers)

        # !) call this functions after adding all routers
        _check_routes(self)
        _use_route_names_as_operation_ids(self)

    # Keep a generic context.
    memo: Memo = None


def _init_context_routers(server: FastAPI):
    router = APIRouter()

    @router.get("/context")
    def context():
        return server.memo.context

    @router.get("/schema")
    def schema():
        return json.loads(server.memo.context.schema_json())

    @router.get("/context/{hid}")
    def value(hid: str):
        return getattr(server.memo.context, hid)

    # See [schema].
    @router.put("/context/{hid}/{value}")
    def put_inline_hid_value(hid: str, value: str):
        setattr(server.memo.context, hid, value)
        return True

    # See [schema].
    @router.put("/context/{hid}")
    def put_inline_hid_json_value(
        hid: str,
        value: str = Body(embed=True),
    ):
        setattr(server.memo.context, hid, value)
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
        setattr(server.memo.context, hid, value)
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

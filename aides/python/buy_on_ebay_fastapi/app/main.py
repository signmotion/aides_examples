from fastapi import FastAPI
from fastapi.routing import APIRoute
from .routers import about, context, products_today


# ! See conventions in ../README.md.

app = FastAPI(title="Auction eBay Aide")

app.include_router(about.router)
app.include_router(context.router)
app.include_router(products_today.router)


# the aide character section
# See `routers/about.py`.


# the context section
# See `routers/context.py`.


# the abilities section
# See `routers/*.py`.


# TODO Move to separate library. See `base_server`.
# TODO Add to other FastApi-projects into the same folder.
# Check the declared routes.
def check_routes(app: FastAPI) -> None:
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"\n\n{route}")

            if route.path.lower() != route.path:
                raise Exception("The route API should be declared in lowercase.")

            if route.name != "root" and "{" not in route.path:
                tpath = route.path[1:].replace("_", "-").replace("/", "-").lower()
                if tpath != route.name.replace("_", "-"):
                    raise Exception(
                        "The route API should be declared with `-` instead of `_`"
                        " and it should have the same names for path and name."
                        f" Have: `{tpath}` != `{route.name}`."
                    )


# Simplify operation IDs into the routes.
def use_route_names_as_operation_ids(app: FastAPI) -> None:
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"{route.operation_id} -> {route.name}")
            route.operation_id = route.name


# !) call the functions after adding all your path operations
check_routes(app)
use_route_names_as_operation_ids(app)

from fastapi import routing


def skip_check_route(route: routing.APIRoute) -> bool:
    return (
        route.name == "root"
        or "asyncapi" in route.path
        or "/context" in route.path
        or "{" in route.path
    )

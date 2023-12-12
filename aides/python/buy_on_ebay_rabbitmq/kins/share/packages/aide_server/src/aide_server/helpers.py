from typing import Dict, List
from fastapi import routing


def skip_check_route(route: routing.APIRoute) -> bool:
    return (
        route.name == "root"
        or "asyncapi" in route.path
        or "/context" in route.path
        or "{" in route.path
    )


def unwrapMultilangText(
    multilangText: Dict[str, str],
    language: str,
) -> str:
    return multilangText.get(language) or ""


def unwrapMultilangTextList(
    multilangTextList: List[Dict[str, str]],
    language: str,
) -> List[str]:
    return [
        unwrapMultilangText(mlt, language)
        for mlt in multilangTextList
        if language in mlt
    ]

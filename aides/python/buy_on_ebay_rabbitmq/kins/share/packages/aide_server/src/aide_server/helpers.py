from fastapi import routing
from .log import logger
import traceback
from typing import Any, Dict, List, Optional


def construct_answer(
    mapped_result: Optional[Dict[str, Any]] = None,
    improved_result: Optional[Dict[str, Any]] = None,
    raw_result: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None,
) -> Dict[str, Any]:
    o = {}

    if bool(mapped_result):
        o["mapped_result"] = mapped_result

    if bool(improved_result):
        o["improved_result"] = improved_result

    if bool(raw_result) or (not bool(improved_result) and not bool(mapped_result)):
        o["raw_result"] = raw_result

    if bool(context):
        o["context"] = context

    if error:
        logger.error(error)
        o["error"] = {
            "key": f"{error}",
            "traceback": f"{traceback.format_exc()}",
        }

    return o


def skip_check_route(route: routing.APIRoute) -> bool:
    return (
        route.name == "root"
        or "asyncapi" in route.path
        or "/context" in route.path
        or "{" in route.path
    )


def unwrap_multilang_text(
    multilangText: Dict[str, str],
    language: str,
) -> str:
    return multilangText.get(language) or multilangText.get("en") or ""


def unwrap_multilang_text_list(
    multilangTextList: List[Dict[str, str]],
    language: str,
) -> List[str]:
    return [unwrap_multilang_text(mlt, language) for mlt in multilangTextList]

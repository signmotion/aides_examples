from fastapi import routing
from pydantic import NonNegativeFloat
from .log import logger
import traceback
from typing import Any, Callable, Dict, List, Optional

from .task_progress_result import Result, Task


def construct_answer(
    mapped_result: Optional[Dict[str, Any]] = None,
    improved_result: Optional[Any] = None,
    raw_result: Optional[Any] = None,
    context: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None,
) -> Dict[str, Any]:
    """
    The order keys into JSON-answer:
        - error
        - mapped
        - improved
        - raw
        - context
    """
    o = {}

    if error:
        logger.error(error)
        o["error"] = {
            "key": f"{error}",
            "traceback": f"{traceback.format_exc()}",
        }

    if bool(mapped_result):
        o["mapped_result"] = mapped_result

    if bool(improved_result):
        o["improved_result"] = improved_result

    if bool(raw_result) or (not bool(improved_result) and not bool(mapped_result)):
        o["raw_result"] = raw_result

    if bool(context):
        o["context"] = context

    return o


async def construct_and_publish(
    task: Task,
    publish_progress: Callable,
    publish_result: Callable,
    construct_raw_result: Callable,
    construct_improved_result: Optional[Callable] = None,
    construct_mapped_result: Optional[Callable] = None,
    include_raw_response_in_answer: bool = True,
    include_context_in_answer: bool = True,
    start_progress_raw_result: NonNegativeFloat = 100.0 / 3 * 0,
    start_progress_improved_result: NonNegativeFloat = 100.0 / 3 * 1,
    start_progress_mapped_result: NonNegativeFloat = 100.0 / 3 * 2,
    fake_raw_result: Optional[Any] = None,
):
    raw_result: Optional[Any] = None
    improved_result: Optional[Any] = None
    mapped_result: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    while True:
        try:
            await publish_progress(task, start_progress_raw_result)
            raw_result = fake_raw_result or construct_raw_result(
                task=task,
                publish_progress=publish_progress,
                publish_result=publish_result,
                start_progress=start_progress_raw_result,
                stop_progress=start_progress_improved_result - 1,
            )
            await publish_progress(task, start_progress_improved_result - 1)

            if construct_improved_result:
                await publish_progress(task, start_progress_improved_result)
                improved_result = construct_improved_result(
                    source=raw_result,
                    task=task,
                    publish_progress=publish_progress,
                    publish_result=publish_result,
                    start_progress=start_progress_improved_result,
                    stop_progress=start_progress_mapped_result - 1,
                )
            await publish_progress(task, start_progress_mapped_result - 1)

            if construct_mapped_result:
                await publish_progress(task, start_progress_mapped_result)
                mapped_result = construct_mapped_result(
                    source=improved_result,
                    task=task,
                    publish_progress=publish_progress,
                    publish_result=publish_result,
                    start_progress=start_progress_mapped_result,
                    stop_progress=100.0 - 1,
                )
            await publish_progress(task, 100.0 - 1)

            break

        except Exception as ex:
            logger.error(f"{ex} :: {traceback.format_exc()}")
            error = ex

            break

    value = construct_answer(
        mapped_result=mapped_result,
        improved_result=improved_result,
        raw_result=raw_result if include_raw_response_in_answer else None,
        context=task.context if include_context_in_answer else None,
        error=error,
    )

    await publish_progress(task, 100)

    return await publish_result(
        task,
        Result(uid_task=task.uid, value=value),
    )


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

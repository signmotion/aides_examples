from fastapi import routing
from pydantic import NonNegativeFloat, NonNegativeInt
import traceback
from typing import Any, Awaitable, Callable, Dict, List, Optional

from .log import logger
from .task_progress_result import Result, Task

from ....short_json.src.short_json.short_json import short_json


# (task, progress)
PublishProgressFn = Callable[[Task, NonNegativeFloat], Awaitable[NonNegativeFloat]]

# (task, result)
PublishResultFn = Callable[[Task, Any], Awaitable[Any]]

# (task, publish_progress, publish_result, start_progress, stop_progress)
ConstructRawResult = Callable[
    [
        Task,
        PublishProgressFn,
        PublishResultFn,
        NonNegativeFloat,
        NonNegativeFloat,
    ],
    Awaitable[Any],
]

# (task, raw_result, publish_progress, publish_result, start_progress, stop_progress)
ConstructImprovedResult = Callable[
    [
        Task,
        Any,
        PublishProgressFn,
        PublishResultFn,
        NonNegativeFloat,
        NonNegativeFloat,
    ],
    Awaitable[Any],
]

# (task, raw_result, improved_result, publish_progress, publish_result, start_progress, stop_progress)
ConstructMappedResult = Callable[
    [
        Task,
        Any,
        Any,
        PublishProgressFn,
        PublishResultFn,
        NonNegativeFloat,
        NonNegativeFloat,
    ],
    Awaitable[Dict[str, Any]],
]

# (task, publish_progress, publish_result)
RunFn = Callable[[Task, PublishProgressFn, PublishResultFn], Awaitable[None]]


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
        - mapped_result
        - improved_result
        - raw_result
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
    act_hid: str,
    task: Task,
    publish_progress: PublishProgressFn,
    publish_result: PublishResultFn,
    construct_raw_result: ConstructRawResult,
    construct_improved_result: Optional[ConstructImprovedResult] = None,
    construct_mapped_result: Optional[ConstructMappedResult] = None,
    include_raw_response_in_answer: bool = True,
    include_context_in_answer: bool = True,
    start_progress_raw_result: NonNegativeFloat = 100.0 / 3 * 0,
    stop_progress_raw_result: NonNegativeFloat = 100.0 / 3 * 1 - 1,
    start_progress_improved_result: NonNegativeFloat = 100.0 / 3 * 1,
    stop_progress_improved_result: NonNegativeFloat = 100.0 / 3 * 2 - 1,
    start_progress_mapped_result: NonNegativeFloat = 100.0 / 3 * 2,
    stop_progress_mapped_result: NonNegativeFloat = 100.0 / 3 * 3 - 1,
    fake_raw_result: Optional[Any] = None,
    count_attempts_for_get_result: NonNegativeInt = 1,
):
    logger.info(f"Running act `{act_hid}` with task `{short_json(task)}`...")

    if fake_raw_result:
        logger.warn("Use a fake result.")

    count_request_errors = 0

    raw_result: Optional[Any] = None
    improved_result: Optional[Any] = None
    mapped_result: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    while True:
        try:
            await publish_progress(task, start_progress_raw_result)
            raw_result = fake_raw_result or await construct_raw_result(
                task,
                publish_progress,
                publish_result,
                start_progress_raw_result,
                stop_progress_raw_result,
            )
            await publish_progress(task, stop_progress_raw_result)

            if construct_improved_result:
                await publish_progress(task, start_progress_improved_result)
                improved_result = await construct_improved_result(
                    task,
                    raw_result,
                    publish_progress,
                    publish_result,
                    start_progress_improved_result,
                    stop_progress_improved_result,
                )
                await publish_progress(task, stop_progress_improved_result)

            if construct_mapped_result:
                await publish_progress(task, start_progress_mapped_result)
                mapped_result = await construct_mapped_result(
                    task,
                    raw_result,
                    improved_result,
                    publish_progress,
                    publish_result,
                    start_progress_mapped_result,
                    stop_progress_mapped_result,
                )
                await publish_progress(task, stop_progress_mapped_result)

            break

        except Exception as ex:
            count_request_errors += 1
            logger.warn(
                f"ATTEMPT {count_request_errors} {ex} :: {traceback.format_exc()}"
            )
            error = ex
            if count_request_errors >= count_attempts_for_get_result:
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


# T = TypeVar("T")


# async def async_wrapper(value: T) -> Awaitable[T]:
#     def wrapper(value: T) -> T:
#         return value

#     return asyncio.run(wrapper(value))  # type: ignore


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

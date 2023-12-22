import json
from typing import Any, Callable, Dict

from pydantic import NonNegativeFloat

from ..config import *
from ..packages.aide_server.src.aide_server.helpers import construct_and_publish
from ..packages.aide_server.src.aide_server.log import logger
from ..packages.aide_server.src.aide_server.task_progress_result import Task


async def who_and_how_can_help(
    task: Task,
    publish_progress: Callable,
    publish_result: Callable,
):
    logger.info(f"Running `{__name__}`...")

    return construct_and_publish(
        task,
        construct_raw_result=_construct_raw_result,
        construct_improved_result=_construct_improved_result,
        construct_mapped_result=_construct_mapped_result,
        publish_progress=publish_progress,
        publish_result=publish_result,
        fake_raw_result=_example_response_1() if fake_response else None,
    )


def _construct_raw_result(
    task: Task,
    publish_progress: Callable,
    publish_result: Callable,
    start_progress: NonNegativeFloat,
    stop_progress: NonNegativeFloat,
) -> Any:
    # TODO

    return "TODO"


def _construct_improved_result(
    source: Any,
    task: Task,
    publish_progress: Callable,
    publish_result: Callable,
    start_progress: NonNegativeFloat,
    stop_progress: NonNegativeFloat,
) -> Any:
    # TODO

    return source


def _construct_mapped_result(
    source: Any,
    task: Task,
    publish_progress: Callable,
    publish_result: Callable,
    start_progress: NonNegativeFloat,
    stop_progress: NonNegativeFloat,
) -> Dict[str, Any]:
    # TODO

    return source


def _example_response_1() -> Dict[str, Any]:
    with open("kins/share/data/examples/responses/products_today_1.json", "r") as file:
        data = file.read()

    return json.loads(data)

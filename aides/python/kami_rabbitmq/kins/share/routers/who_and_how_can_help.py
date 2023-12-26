from gpt4all import GPT4All
import json
from pydantic import NonNegativeFloat
from typing import Any, Awaitable, Dict


from ..config import fake_response
from ..packages.aide_server.src.aide_server.helpers import (
    construct_and_publish,
    PublishProgressFn,
    PublishResultFn,
)
from ..packages.aide_server.src.aide_server.log import logger
from ..packages.aide_server.src.aide_server.task_progress_result import Task


async def who_and_how_can_help(
    task: Task,
    publish_progress: PublishProgressFn,
    publish_result: PublishResultFn,
):
    logger.info(f"Running `{__name__}`...")

    return await construct_and_publish(
        __name__,
        task=task,
        construct_raw_result=_construct_raw_result,
        construct_improved_result=_construct_improved_result,
        construct_mapped_result=_construct_mapped_result,  # type: ignore
        publish_progress=publish_progress,
        publish_result=publish_result,
        fake_raw_result=_example_response_1() if fake_response else None,
    )


async def _construct_raw_result(
    task: Task,
    publish_progress: PublishProgressFn,
    publish_result: PublishResultFn,
    start_progress: NonNegativeFloat,
    stop_progress: NonNegativeFloat,
) -> Awaitable[Any]:
    logger.error("Demo GPT4All")

    model = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
    # model = GPT4All("mistral-7b-openorca.Q4_0.gguf")
    output = model.generate("The capital of France is ", max_tokens=3)
    logger.info(output)

    # TODO

    return "TODO"  # type: ignore


async def _construct_improved_result(
    task: Task,
    raw_result: Any,
    publish_progress: PublishProgressFn,
    publish_result: PublishResultFn,
    start_progress: NonNegativeFloat,
    stop_progress: NonNegativeFloat,
) -> Awaitable[Any]:
    # TODO

    return None  # type: ignore


async def _construct_mapped_result(
    task: Task,
    raw_result: Any,
    improved_result: Any,
    publish_progress: PublishProgressFn,
    publish_result: PublishResultFn,
    start_progress: NonNegativeFloat,
    stop_progress: NonNegativeFloat,
) -> Awaitable[Dict[str, Any]]:
    # TODO

    return {}  # type: ignore


def _example_response_1() -> Dict[str, Any]:
    with open("kins/share/data/examples/responses/products_today_1.json", "r") as file:
        data = file.read()

    return json.loads(data)

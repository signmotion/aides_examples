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
        construct_mapped_result=_construct_mapped_result,
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
):
    logger.warn("Demo GPT4All")
    model_name = "mistral-7b-openorca.Q4_0.gguf"
    model_path = f"kins/share/data/models/llms"
    logger.info(f"Connected to model `{model_path}`...")
    model = GPT4All(
        model_name,
        model_path=model_path,
        allow_download=False,
        verbose=True,
    )
    output = model.generate(
        "The capital of France is ",
        temp=0,
        max_tokens=120,
    )
    logger.info(output)

    # TODO

    return output


async def _construct_improved_result(
    task: Task,
    raw_result: Any,
    publish_progress: PublishProgressFn,
    publish_result: PublishResultFn,
    start_progress: NonNegativeFloat,
    stop_progress: NonNegativeFloat,
):
    # TODO

    return None


async def _construct_mapped_result(
    task: Task,
    raw_result: Any,
    improved_result: Any,
    publish_progress: PublishProgressFn,
    publish_result: PublishResultFn,
    start_progress: NonNegativeFloat,
    stop_progress: NonNegativeFloat,
):
    # TODO

    return {}  # type: ignore


def _example_response_1() -> Dict[str, Any]:
    with open("kins/share/data/examples/responses/products_today_1.json", "r") as file:
        data = file.read()

    return json.loads(data)

import logging
from typing import Callable, List
from fastapi import APIRouter
from pydantic import Field, PositiveFloat

from .side import Side
from ..act import Act
from ..memo import Memo, NoneMemo
from ..savant_router import SavantRouter
from ..task import Task

logger = logging.getLogger("uvicorn.error")


class BrainSide(Side):
    def __init__(
        self,
        router: APIRouter,
        savant_router: SavantRouter,
        acts: List[Act],
        runs: List[Callable],
        memo: Memo,
    ):
        super().__init__(
            router=router,
            savant_router=savant_router,
            acts=acts,
        )

        self.runs = runs
        self.memo = memo

        self.register_subscribers_for_acts()

    runs: List[Callable] = Field(
        ...,
        title="Braint Runs",
        description="The runs for Brain server. Each runs should be defined into `configure.json` with same name.",
    )

    memo: Memo = Field(
        default=NoneMemo(),
        title="Memo",
        description="The memory of aide. Keep a generic context.",
    )

    def register_subscribers_for_acts(self):
        logger.info("Registering subscribers for act(s)...")

        for act in self.acts:
            self.register_subscribers_for_act(act)

        logger.info(f"Registered subscribers for {len(self.acts)} act(s)...")

    def register_subscribers_for_act(self, act: Act):
        queue = self.savant_router.queryQueue(act.nickname)
        exchange = self.savant_router.exchange()

        @self.savant_router.broker.subscriber(queue, exchange)
        async def catch_task(task: Task):
            logger.info(f"Catched task {type(task).__name__} -> {task}")
            if isinstance(task, dict):
                task = Task.model_validate(task)  # type: ignore
            self.run_task(task)

        logger.info(f"Registered subscribers for act `{act.nickname}` to Savant.")

    # def catch_task(self):
    #     pass

    def run_task(self, task: Task):
        found_run = None
        for run in self.runs:
            logger.info(
                f"Looking at act `{task.nickname_act}` into run `{run.__name__}`..."
            )
            if task.nickname_act in run.__name__:
                logger.info(f"Run for act `{task.nickname_act}` found.")
                found_run = run
                break

        if not found_run:
            raise Exception(f"Not found a run for act {task.nickname_act}.")

        found_run(
            task=task,
            memo=self.memo,
            publish_progress=self.publish_progress,
            publish_result=self.publish_result,
        )

    def publish_progress(self, task: Task, progress: PositiveFloat):
        logger.info(f"Progress for task `{task}`: {progress} %")
        # TODO

        return progress

    def publish_result(self, task: Task, result: dict):
        logger.info(f"Result for task `{task}`: `{result}`")
        # TODO

        return result

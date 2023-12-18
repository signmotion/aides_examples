from fastapi import APIRouter
from pydantic import Field, NonNegativeFloat
import time
from typing import Any, Callable, List

from .side import Side

from ..act import Act
from ..inner_memo import NoneInnerMemo
from ..log import logger
from ..savant_router import SavantRouter
from ..task import Progress, Result, Task


class BrainSide(Side):
    def __init__(
        self,
        router: APIRouter,
        savant_router: SavantRouter,
        acts: List[Act],
        runs: List[Callable],
    ):
        assert bool(runs)
        assert len(runs) == len(acts)

        super().__init__(
            router=router,
            savant_router=savant_router,
            acts=acts,
            inner_memo=NoneInnerMemo(),
        )

        self.runs = runs

        self._register_catchers_for_acts()

        logger.info(
            f"🏳️‍🌈 Initialized `{self.name}` with runs `{self.runs}`"
            f" and inner memo `{self.inner_memo}`."
        )

    runs: List[Callable] = Field(
        ...,
        title="Braint Runs",
        description="The runs for Brain server. Each runs should be defined into `configure.json` with same name.",
    )

    def _register_catchers_for_acts(self):
        logger.info("🪶 Registering catchers for act(s)...")

        for act in self.acts:
            self._register_catchers_for_act(act)

        logger.info(f"🪶 Registered catchers for {len(self.acts)} act(s).")

    def _register_catchers_for_act(self, act: Act):
        n = 1

        @self.savant_router.broker.subscriber(
            queue=self.savant_router.taskQueue(act.hid),
            exchange=self.savant_router.exchange(),
        )
        async def task_catcher(task: Task):
            logger.info(f"Catched a task {type(task).__name__} -> {task}")
            if isinstance(task, dict):
                task = Task.model_validate(task)
            await self._run_task(task)

        logger.info(f"🪶 Registered {n} catcher for act `{act.hid}`.")

    async def _run_task(self, task: Task):
        found_run = None
        for run in self.runs:
            logger.info(f"Looking at act `{task.hid_act}` into run `{run.__name__}`...")
            if task.hid_act in run.__name__:
                logger.info(f"Run for act `{task.hid_act}` found.")
                found_run = run
                break

        if not found_run:
            raise Exception(f"Not found a run for task `{task}`.")

        await found_run(
            task=task,
            publish_progress=self.publish_progress,
            publish_result=self.publish_result,
        )

    # catcher: Keeper
    async def publish_progress(self, task: Task, progress: NonNegativeFloat):
        logger.info(f"Progress for task `{task}`: {progress} %")

        exchange = self.savant_router.exchange()
        queue = self.savant_router.progressQueue(task.hid_act)

        logger.info(
            f"Publish a progress of task `{task}` to Savant:"
            f" exchange `{exchange.name}`, queue `{queue.name}`."
        )
        await self.savant_router.broker.publish(
            Progress(uid_task=task.uid, value=progress),
            queue=queue,
            exchange=exchange,
            timeout=6,
        )

        time.sleep(2)

        return progress

    # catcher: Keeper
    async def publish_result(self, task: Task, result: Any):
        logger.info(f"Result for task `{task}`: `{result}`")

        exchange = self.savant_router.exchange()
        queue = self.savant_router.resultQueue(task.hid_act)

        logger.info(
            f"Publish a result of task `{task}` to Savant:"
            f" exchange `{exchange.name}`, queue `{queue.name}`."
        )
        await self.savant_router.broker.publish(
            Result(uid_task=task.uid, value=result),
            queue=queue,
            exchange=exchange,
            timeout=6,
        )

        time.sleep(2)

        return result
from fastapi import APIRouter
from pydantic import Field, NonNegativeFloat
import time
from typing import Any, List
from faststream.rabbit import RabbitQueue

from .side import Side
from .type_side import TypeSide

from ..act import Act
from ..helpers import RunFn
from ..inner_memo import NoneInnerMemo
from ..log import logger
from ..savant_router import SavantRouter
from ..task_progress_result import Progress, Result, Task


from .....short_json.src.short_json.short_json import short_json


class BrainSide(Side):
    def __init__(
        self,
        router: APIRouter,
        savant_router: SavantRouter,
        acts: List[Act],
        runs: List[RunFn],
    ):
        assert bool(runs), "The runs should be able, as least 1."
        if len(runs) != len(acts):
            logger.warn(
                f"The count of runs ({len(runs)})"
                f" doesn't much the count of acts ({len(acts)})."
            )

        super().__init__(
            router=router,
            savant_router=savant_router,
            acts=acts,
            inner_memo=NoneInnerMemo(),
        )

        self.runs = runs

        self._register_catchers_for_acts()

        logger.info(
            f"🏳️‍🌈 Initialized `{self.type.name}` with runs `{self.runs}`"
            f" and inner memo `{self.inner_memo}`."
        )

    runs: List[RunFn] = Field(
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

        @self.taskCatcher(
            act.hid,
            pusher_side=TypeSide.APPEARANCE,
            catcher_side=self.type,
        )
        async def task_catcher(task: Task):
            ts = short_json(task, exclude={"context"})
            logger.info(f"Catched a task {type(task).__name__} -> {ts}")
            if isinstance(task, dict):
                task = Task.model_validate(task)
            await self._run_task(task)

        logger.info(f"🪶 Registered {n} catcher for act `{act.hid}`.")

    async def _run_task(self, task: Task):
        found_run = None
        for run in self.runs:
            logger.info(f"Looking at act `{task.hid_act}` into run `{run.__name__}`...")
            if task.hid_act in run.__name__:
                logger.info(f"A run for act `{task.hid_act}` found.")
                found_run = run
                break

        if not found_run:
            ts = short_json(task, exclude={"context"})
            raise Exception(f"Not found a run for task `{ts}`.")

        await found_run(
            task,
            self.publish_progress,
            self.publish_result,
        )

    # catcher: Keeper, [Appearance]
    async def publish_progress(
        self, task: Task, progress: NonNegativeFloat
    ) -> NonNegativeFloat:
        await self._publish_progress(
            task=task,
            progress=progress,
            queue=self.savant_router.progressQueue(
                task.hid_act,
                pusher_side=TypeSide.BRAIN,
                catcher_side=TypeSide.KEEPER,
            ),
        )

        await self._publish_progress(
            task=task,
            progress=progress,
            queue=self.savant_router.progressQueue(
                task.hid_act,
                pusher_side=TypeSide.BRAIN,
                catcher_side=TypeSide.APPEARANCE,
            ),
        )

        return progress

    async def _publish_progress(
        self,
        task: Task,
        progress: NonNegativeFloat,
        queue: RabbitQueue,
    ):
        ts = short_json(task, exclude={"context"})
        p = "{:.2f}".format(progress.real)
        logger.info(f"Progress for task `{ts}`: {p}%")

        logger.info(
            f"Publish a progress of task `{task.hid_act}` to Savant:"
            f" queue `{queue.name}`."
        )
        await self.push(
            Progress(uid_task=task.uid, value=progress),
            queue=queue,
        )

        # test
        time.sleep(0.2)

        return progress

    # catcher: Keeper, [Appearance]
    async def publish_result(self, task: Task, result: Any) -> Any:
        await self._publish_result(
            task=task,
            result=result,
            queue=self.savant_router.resultQueue(
                task.hid_act,
                pusher_side=TypeSide.BRAIN,
                catcher_side=TypeSide.KEEPER,
            ),
        )

        await self._publish_result(
            task=task,
            result=result,
            queue=self.savant_router.resultQueue(
                task.hid_act,
                pusher_side=TypeSide.BRAIN,
                catcher_side=TypeSide.APPEARANCE,
            ),
        )

        return result

    async def _publish_result(
        self,
        task: Task,
        result: Any,
        queue: RabbitQueue,
    ):
        ts = short_json(task, exclude={"context"})
        logger.info(
            f"Publish in Savant queue `{queue.name}`"
            f"\n\tfor task `{ts}`:"
            f"\n\tresult`{short_json(result)}`"
        )
        await self.push(
            Result(uid_task=task.uid, value=result),
            queue=queue,
        )

        # test
        time.sleep(0.2)

        return result

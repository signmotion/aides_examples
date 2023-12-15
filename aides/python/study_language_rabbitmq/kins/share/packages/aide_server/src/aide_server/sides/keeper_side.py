import json
from fastapi import APIRouter
from typing import List

from .side import Side

from ..act import Act
from ..inner_memo import InnerMemo, NoneInnerMemo
from ..log import logger
from ..savant_router import SavantRouter
from ..task import Progress, Result


class KeeperSide(Side):
    def __init__(
        self,
        router: APIRouter,
        savant_router: SavantRouter,
        acts: List[Act],
        inner_memo: InnerMemo,
    ):
        assert not isinstance(
            self.inner_memo, NoneInnerMemo
        ), "The Keeper should have an inner memo."

        super().__init__(
            router=router,
            savant_router=savant_router,
            acts=acts,
            inner_memo=inner_memo,
        )

        self._register_catchers_for_acts()

        logger.info(
            f"🏳️‍🌈 Initialized `{self.name}` with inner memory `{self.inner_memo}`."
        )

    def _register_catchers_for_acts(self):
        logger.info("🪶 Registering catchers for act(s)...")

        for act in self.acts:
            self._register_catchers_for_act(act)

        logger.info(f"🪶 Registered catchers for {len(self.acts)} act(s).")

    def _register_catchers_for_act(self, act: Act):
        n = 1

        @self.savant_router.broker.subscriber(
            queue=self.savant_router.progressQueue(act.hid),
            exchange=self.savant_router.exchange(),
        )
        async def progress_catcher(progress: Progress):
            logger.info(f"Catched a progress `{progress}`.")
            if isinstance(progress, dict):
                progress = Progress.model_validate(progress)
            self._progress_catched(progress)

        n += 1

        # TODO Replace to `self.savant_broker.subscriber()` or `self.catcher()`.
        @self.savant_router.broker.subscriber(
            queue=self.savant_router.resultQueue(act.hid),
            exchange=self.savant_router.exchange(),
        )
        async def result_catcher(result: Result):
            logger.info(f"Catched a result `{result}`.")
            if isinstance(result, dict):
                result = Result.model_validate(result)
            await self._result_catched(result)

        n += 1

        @self.savant_router.broker.subscriber(
            queue=self.savant_router.requestProgressQueue(),
            exchange=self.savant_router.exchange(),
        )
        async def request_progress_catcher(uid_task: str):
            logger.info(f"Catched a request progress for task `{uid_task}`.")
            await self._request_progress_catched(uid_task)

        n += 1

        @self.savant_router.broker.subscriber(
            queue=self.savant_router.requestResultQueue(),
            exchange=self.savant_router.exchange(),
        )
        async def request_result_catcher(uid_task: str):
            logger.info(f"Catched a request result for task `{uid_task}`.")
            await self._request_result_catched(uid_task)

        logger.info(f"🪶 Registered {n} catchers for act `{act.hid}`.")

    def _progress_catched(self, progress: Progress):
        key = f"{progress.uid_task}.progress"
        self.inner_memo.put(key, progress.value)

    async def _result_catched(self, result: Result):
        key = f"{result.uid_task}.result"
        self.inner_memo.put(key, result.value)

    async def _request_progress_catched(self, uid_task: str):
        key = f"{uid_task}.progress"
        value = self.inner_memo.get(key)
        await self._publish_response_progress(uid_task, value=float(value))

    async def _request_result_catched(self, uid_task: str):
        key = f"{uid_task}.result"
        value = self.inner_memo.get(key)
        await self._publish_response_result(uid_task, value=json.loads(value))

    # catcher: Appearance
    async def _publish_response_progress(self, uid_task: str, value: float):
        exchange = self.savant_router.exchange()
        queue = self.savant_router.responseProgressQueue()

        logger.info(
            f"Publish a response progress for task `{uid_task}` to Savant:"
            f" exchange `{exchange.name}`, queue `{queue.name}`."
        )
        # TODO Replace to `self.savant_broker.publish()` or `self.publish()`.
        await self.savant_router.broker.publish(
            Progress(uid_task=uid_task, value=value),
            queue=queue,
            exchange=exchange,
            timeout=6,
        )

        return True

    # catcher: Appearance
    async def _publish_response_result(self, uid_task: str, value: str):
        exchange = self.savant_router.exchange()
        queue = self.savant_router.responseResultQueue()

        logger.info(
            f"Publish a response result for task `{uid_task}` to Savant:"
            f" exchange `{exchange.name}`, queue `{queue.name}`."
        )
        # TODO Replace to `self.savant_broker.publish()` or `self.publish()`.
        await self.savant_router.broker.publish(
            Result(uid_task=uid_task, value=value),
            queue=queue,
            exchange=exchange,
            timeout=6,
        )

        return True

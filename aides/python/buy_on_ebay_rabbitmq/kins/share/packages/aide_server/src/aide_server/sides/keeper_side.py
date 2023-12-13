from typing import List
from fastapi import APIRouter
from pydantic import Field

from .side import Side
from ..act import Act
from ..keeper_brokers.keeper_broker import KeeperBroker
from ..log import logger
from ..savant_router import SavantRouter
from ..task import Progress, Result


class KeeperSide(Side):
    def __init__(
        self,
        router: APIRouter,
        savant_router: SavantRouter,
        acts: List[Act],
        keeper_broker: KeeperBroker,
    ):
        super().__init__(
            router=router,
            savant_router=savant_router,
            acts=acts,
        )

        self.keeper_broker = keeper_broker

        self.register_catchers_for_acts()

        logger.info(
            f"🏳️‍🌈 Initialized `{self.name}` with keeper broker `{self.keeper_broker}`."
        )

    keeper_broker: KeeperBroker = Field(
        ...,
        title="Keeper Broker",
        description="The broker for save and load data.",
    )

    def register_catchers_for_acts(self):
        logger.info("🪶 Registering catchers for act(s)...")

        for act in self.acts:
            self.register_catchers_for_act(act)

        logger.info(f"🪶 Registered catchers for {len(self.acts)} act(s).")

    def register_catchers_for_act(self, act: Act):
        n = 1

        @self.savant_router.broker.subscriber(
            queue=self.savant_router.progressQueue(act.hid),
            exchange=self.savant_router.exchange(),
        )
        async def progress_catcher(progress: Progress):
            logger.info(f"Catched a progress `{progress}`.")
            if isinstance(progress, dict):
                progress = Progress.model_validate(progress)
            self.progress_catched(progress)

        n += 1

        @self.savant_router.broker.subscriber(
            queue=self.savant_router.resultQueue(act.hid),
            exchange=self.savant_router.exchange(),
        )
        async def result_catcher(result: Result):
            logger.info(f"Catched a result `{result}`.")
            if isinstance(result, dict):
                result = Result.model_validate(result)
            self.result_catched(result)

        logger.info(f"🪶 Registered {n} catchers for act `{act.hid}`.")

    def progress_catched(self, progress: Progress):
        key = f"{progress.uid_task}.progress"
        self.keeper_broker.put(key, progress.value)

    def result_catched(self, result: Result):
        key = f"{result.uid_task}.result"
        self.keeper_broker.put(key, result.value)

    # def catch_progress(self):
    #     pass

    # def catch_result(self):
    #     pass

    def catch_requested_progress(self):
        pass

    def publish_requested_progress(self):
        pass

    def catch_requested_result(self):
        pass

    def publish_request_result(self):
        pass

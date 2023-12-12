import logging
from typing import Callable, List
from fastapi import APIRouter
from pydantic import Field

from .side import Side
from ..act import Act
from ..memo import Memo, NoneMemo
from ..savant_router import SavantRouter

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
        async def catch_task(message: str):
            logger.info("Catch task!")
            self.run_act(act)

        logger.info(f"Registered subscribers for act `{act.nickname}` to Savant.")

    # def catch_task(self):
    #     pass

    def run_act(self, act: Act):
        found_run = None
        for run in self.runs:
            for act in self.acts:
                logger.info(f"`{act.nickname}` in `{run}`?")
                if act.nickname in run.__str__():
                    logger.info(f"Run for act `{act.nickname}` found.")
                    found_run = run
                    break

        if found_run:
            found_run(self.memo)
        else:
            raise Exception(f"Not found a brain-run for {act}.")

    def publish_progress(self):
        pass

    def publish_result(self):
        pass

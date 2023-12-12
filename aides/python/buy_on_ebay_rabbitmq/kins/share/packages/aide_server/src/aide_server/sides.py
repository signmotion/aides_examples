import logging
from typing import Callable, List
from fastapi import APIRouter
from pydantic import Field

from .act import Act
from .memo import Memo, NoneMemo
from .savant_router import SavantRouter

logger = logging.getLogger("uvicorn.error")


# Functional part of server: endpoints, tasks, etc.
class Side:
    def __init__(
        self,
        router: APIRouter,
        savant_router: SavantRouter,
        acts: List[Act],
    ):
        self.name = type(self).__name__.rstrip("Side")
        self.router = router
        self.savant_router = savant_router
        self.acts = acts

    name: str = Field(
        ...,
        title="Name",
        description="The name for side of aide. Set by class.",
    )

    router: APIRouter = Field(
        ...,
        title="Router",
        description="The router for set of acts.",
    )

    savant_router: SavantRouter = Field(
        ...,
        title="Savant Router",
        description="The router of Savant.",
    )

    acts: List[Act] = Field(
        default=[],
        title="Acts Aide",
        description="Possible acts this aide.",
    )


# Appearance
class AppearanceSide(Side):
    def __init__(
        self,
        router: APIRouter,
        savant_router: SavantRouter,
        acts: List[Act],
    ):
        super().__init__(
            router=router,
            savant_router=savant_router,
            acts=acts,
        )

        for act in self.acts:
            self.register_client_endpoint(act)

    def register_client_endpoint(self, act: Act):
        @self.router.get(act.nickname)
        async def endpoint():
            logger.info(f"Call endpoint `{act.nickname}`")
            await self._publish_task(act)

        logger.info(f"Registered client endpoint for `{act.nickname}`.")

    async def _publish_task(self, act: Act):
        exchange = self.savant_router.exchange()
        queue = self.savant_router.taskQueue(route_name=act.nickname)

        message = act.nickname
        logger.info("Publish task message")
        await self.savant_router.broker.publish(
            message,
            queue=queue,
            exchange=exchange,
            timeout=5,
        )


# Brain
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

        for act in self.acts:
            self.register_subscribers(act)

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

    def register_subscribers(self, act: Act):
        queue = self.savant_router.taskQueue(route_name=act.nickname)
        exchange = self.savant_router.exchange()

        @self.savant_router.broker.subscriber(queue, exchange)
        async def catch_task(message: str):
            logger.info("Catch task!")
            self.run_act(act)

        logger.info(f"Subscribed `{act.nickname}` to Savant.")

    # def catch_task(self):
    #     pass

    def run_act(self, act: Act):
        found_run = None
        for run in self.runs:
            for act in self.acts:
                logger.info(f"`{act.nickname}` in `{run.str()}`?")
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


# Keeper
class KeeperSide:
    # TODO

    def catch_progress(self):
        pass

    def catch_result(self):
        pass

    def catch_requested_progress(self):
        pass

    def publish_requested_progress(self):
        pass

    def catch_requested_result(self):
        pass

    def publish_request_result(self):
        pass

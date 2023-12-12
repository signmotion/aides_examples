import logging
from fastapi import APIRouter

from pydantic import Field

from .act import Act
from .server import AideServer

logger = logging.getLogger("uvicorn.error")


# Functional part of server: endpoints, tasks, etc.
class Side:
    def __init__(
        self,
        router: APIRouter,
        server: AideServer,
    ):
        self.name = type(self).__name__.rstrip("Side")
        self.router = router
        self.server = server

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

    server: AideServer = Field(
        ...,
        title="Server",
        description="The one of servers of aide.",
    )


# Appearance
class AppearanceSide(Side):
    def __init__(
        self,
        router: APIRouter,
        server: AideServer,
    ):
        super().__init__(
            router=router,
            server=server,
        )

        acts = self.server.configure.acts
        for act in acts:
            self.register_client_endpoint(act)

    def register_client_endpoint(self, act: Act):
        @self.router.get(act.nickname)
        async def endpoint():
            logger.info(f"Call endpoint `{act.nickname}`")
            await self._publish_task(act)

        logger.info(f"Registered client endpoint for `{act.nickname}`.")

    async def _publish_task(self, act: Act):
        exchange = self.server.exchange()
        queue = self.server.taskQueue(route_name=act.nickname)

        message = act.nickname
        logger.info("Publish task message")
        await self.server.savant.publish(
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
        server: AideServer,
    ):
        super().__init__(
            router=router,
            server=server,
        )

        acts = self.server.configure.acts
        for act in acts:
            self.register_subscribers(act)

    def register_subscribers(self, act: Act):
        queue = self.server.taskQueue(route_name=act.nickname)
        exchange = self.server.exchange()

        @self.server.savant.subscriber(queue, exchange)
        async def catch_task(message: str):
            logger.info("Catch task!")
            self.run_act(act)

        logger.info(f"Subscribed `{act.nickname}` to Savant.")

    # def catch_task(self):
    #     pass

    def run_act(self, act: Act):
        found_run = None
        for run in self.server.brainRuns:
            for act in self.server.configure.acts:
                logger.info(f"`{act.nickname}` in `{run.str()}`?")
                if act.nickname in run.__str__():
                    logger.info(f"Run for act `{act.nickname}` found.")
                    found_run = run
                    break

        if found_run:
            found_run(self.server.memo)
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

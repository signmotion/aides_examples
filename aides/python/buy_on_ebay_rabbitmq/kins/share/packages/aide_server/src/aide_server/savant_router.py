from typing import List
from faststream.rabbit import (
    ExchangeType,
    RabbitExchange,
    RabbitQueue,
    fastapi,
)
from pydantic import Field
import time
import logging

from .act import Act
from .type_queue import TypeQueue


logger = logging.getLogger("uvicorn.error")


class SavantRouter(fastapi.RabbitRouter):
    def __init__(
        self,
        connector: str,
        nickname_server: str,
        sidename_server: str,
        acts: List[Act],
    ):
        assert connector.strip()
        assert nickname_server.strip()
        assert sidename_server.strip()

        super().__init__(connector)

        self.nickname_server = nickname_server
        self.sidename_server = sidename_server
        self.acts = acts

    nickname_server: str = Field(
        ...,
        title="Nickname Server",
        description="The nickname of server.",
    )

    sidename_server: str = Field(
        ...,
        title="Sidename Server",
        description="The sidename of server.",
    )

    acts: List[Act] = Field(
        default=[],
        title="Acts Aide",
        description="Possible acts this aide.",
    )

    def exchange(self):
        return RabbitExchange(
            "aide",
            auto_delete=True,
            type=ExchangeType.TOPIC,
        )

    def queryQueue(
        self,
        nickname_act: str,
    ):
        return queue(
            type=TypeQueue.QUERY,
            nickname_act=nickname_act,
            nickname_server=self.nickname_server,
        )

    def progressQueue(
        self,
        nickname_act: str,
    ):
        return queue(
            type=TypeQueue.PROGRESS,
            nickname_act=nickname_act,
            nickname_server=self.nickname_server,
        )

    def resultQueue(
        self,
        nickname_act: str,
    ):
        return queue(
            type=TypeQueue.RESULT,
            nickname_act=nickname_act,
            nickname_server=self.nickname_server,
        )

    def requestProgressQueue(self):
        return queue(
            type=TypeQueue.REQUEST_PROGRESS,
            nickname_server=self.nickname_server,
        )

    def requestResultQueue(self):
        return queue(
            type=TypeQueue.REQUEST_RESULT,
            nickname_server=self.nickname_server,
        )

    def responseProgressQueue(self):
        return queue(
            type=TypeQueue.RESPONSE_PROGRESS,
            nickname_server=self.nickname_server,
        )

    def responseResultQueue(self):
        return queue(
            type=TypeQueue.RESPONSE_RESULT,
            nickname_server=self.nickname_server,
        )

    def logQueue(self):
        return queue(
            type=TypeQueue.LOG,
            sidename_server=self.sidename_server,
            nickname_server=self.nickname_server,
        )

    async def declare_exchange(self):
        declare = self.broker.declare_exchange
        ex = self.exchange()
        await declare(ex)
        logger.info(f"Created exchange `{ex.name}` with type `{ex.type.upper()}`.")

    async def declare_queue(self, queue: RabbitQueue):
        await self.broker.declare_queue(queue)
        logger.info(f"\tCreated queue `{queue.name}`.   ")

    async def declare_service_queues(self):
        logger.info(f"Declaring services queues...")

        n = 0
        await self.declare_queue(self.requestProgressQueue())
        n += 1
        await self.declare_queue(self.requestResultQueue())
        n += 1
        await self.declare_queue(self.responseProgressQueue())
        n += 1
        await self.declare_queue(self.responseResultQueue())
        n += 1
        await self.declare_queue(self.logQueue())
        n += 1

        logger.info(f"Declared {n} service(s) queues.")

    async def declare_acts_queues(self):
        logger.info(f"Declaring act(s)...")

        for act in self.acts:
            logger.info(f"Declaring queues for act `{act.name['en']}`...")

            n = 0
            await self.declare_queue(self.queryQueue(act.nickname))
            n += 1
            await self.declare_queue(self.progressQueue(act.nickname))
            n += 1
            await self.declare_queue(self.resultQueue(act.nickname))
            n += 1

            time.sleep(0.2)

            logger.info(f"Declared {n} queue(s) for act `{act.name['en']}`.")

        logger.info(f"Declared {len(self.acts)} act(s).")


def queue(
    type: TypeQueue,
    nickname_act: str = "",
    sidename_server: str = "",
    nickname_server: str = "",
):
    keys = [
        type.name.lower(),
        nickname_act,
        sidename_server.lower() if sidename_server else None,
        nickname_server,
    ]
    name = ".".join(filter(None, keys))

    return RabbitQueue(name, auto_delete=True)

from faststream.rabbit import (
    ExchangeType,
    RabbitExchange,
    RabbitQueue,
    fastapi,
)
from pydantic import Field
import time
from typing import List

from kins.share.packages.aide_server.src.aide_server.sides.type_side import TypeSide

from .act import Act
from .log import logger
from .type_queue import TypeQueue


class SavantRouter(fastapi.RabbitRouter):
    def __init__(
        self,
        connector: str,
        hid_server: str,
        sidename_server: str,
        acts: List[Act],
    ):
        assert connector.strip()
        assert hid_server.strip()
        assert sidename_server.strip()

        super().__init__(connector)

        self.hid_server = hid_server
        self.sidename_server = sidename_server
        self.acts = acts

    hid_server: str = Field(
        ...,
        title="HID Server",
        description="The hid of server.",
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
            timeout=6,
        )

    def taskQueue(
        self,
        hid_act: str,
        pusher_side: TypeSide,
        catcher_side: TypeSide,
    ):
        return queue(
            type=TypeQueue.TASK,
            hid_act=hid_act,
            hid_server=self.hid_server,
            pusher_side=pusher_side,
            catcher_side=catcher_side,
        )

    def progressQueue(
        self,
        hid_act: str,
        pusher_side: TypeSide,
        catcher_side: TypeSide,
    ):
        return queue(
            type=TypeQueue.PROGRESS,
            hid_act=hid_act,
            hid_server=self.hid_server,
            pusher_side=pusher_side,
            catcher_side=catcher_side,
        )

    def resultQueue(
        self,
        hid_act: str,
        pusher_side: TypeSide,
        catcher_side: TypeSide,
    ):
        return queue(
            type=TypeQueue.RESULT,
            hid_act=hid_act,
            hid_server=self.hid_server,
            pusher_side=pusher_side,
            catcher_side=catcher_side,
        )

    def requestProgressQueue(
        self,
        pusher_side: TypeSide,
        catcher_side: TypeSide,
    ):
        return queue(
            type=TypeQueue.REQUEST_PROGRESS,
            hid_server=self.hid_server,
            pusher_side=pusher_side,
            catcher_side=catcher_side,
        )

    def requestResultQueue(
        self,
        pusher_side: TypeSide,
        catcher_side: TypeSide,
    ):
        return queue(
            type=TypeQueue.REQUEST_RESULT,
            hid_server=self.hid_server,
            pusher_side=pusher_side,
            catcher_side=catcher_side,
        )

    def responseProgressQueue(
        self,
        pusher_side: TypeSide,
        catcher_side: TypeSide,
    ):
        return queue(
            type=TypeQueue.RESPONSE_PROGRESS,
            hid_server=self.hid_server,
            pusher_side=pusher_side,
            catcher_side=catcher_side,
        )

    def responseResultQueue(
        self,
        pusher_side: TypeSide,
        catcher_side: TypeSide,
    ):
        return queue(
            type=TypeQueue.RESPONSE_RESULT,
            hid_server=self.hid_server,
            pusher_side=pusher_side,
            catcher_side=catcher_side,
        )

    def logQueue(
        self,
        pusher_side: TypeSide,
        catcher_side: TypeSide,
    ):
        return queue(
            type=TypeQueue.LOG,
            hid_server=self.hid_server,
            pusher_side=pusher_side,
            catcher_side=catcher_side,
        )

    async def declare_exchange(self):
        declare = self.broker.declare_exchange
        ex = self.exchange()
        await declare(ex)
        logger.info(f"🌱 Created exchange `{ex.name}` with type `{ex.type.upper()}`.")

    async def declare_queue(self, queue: RabbitQueue):
        await self.broker.declare_queue(queue)
        logger.info(f"\t🌱 Created queue `{queue.name}`.   ")

    async def declare_service_queues(self):
        logger.info(f"🌱 Declaring services queues...")

        n = 0

        await self.declare_queue(
            self.requestProgressQueue(
                pusher_side=TypeSide.APPEARANCE,
                catcher_side=TypeSide.KEEPER,
            )
        )
        n += 1

        await self.declare_queue(
            self.requestResultQueue(
                pusher_side=TypeSide.APPEARANCE,
                catcher_side=TypeSide.KEEPER,
            )
        )
        n += 1

        await self.declare_queue(
            self.responseProgressQueue(
                pusher_side=TypeSide.APPEARANCE,
                catcher_side=TypeSide.KEEPER,
            )
        )
        n += 1

        await self.declare_queue(
            self.responseResultQueue(
                pusher_side=TypeSide.APPEARANCE,
                catcher_side=TypeSide.KEEPER,
            )
        )
        n += 1

        await self.declare_queue(
            self.logQueue(
                pusher_side=TypeSide.APPEARANCE,
                catcher_side=TypeSide.APPEARANCE,
            )
        )
        n += 1
        await self.declare_queue(
            self.logQueue(
                pusher_side=TypeSide.BRAIN,
                catcher_side=TypeSide.BRAIN,
            )
        )
        n += 1
        await self.declare_queue(
            self.logQueue(
                pusher_side=TypeSide.KEEPER,
                catcher_side=TypeSide.KEEPER,
            )
        )
        n += 1

        logger.info(f"🌱 Declared {n} service(s) queues.")

    async def declare_acts_queues(self):
        logger.info(f"🌱 Declaring act(s)...")

        for act in self.acts:
            logger.info(f"🌱 Declaring queues for act `{act.name['en']}`...")

            n = 0

            await self.declare_queue(
                self.taskQueue(
                    act.hid,
                    pusher_side=TypeSide.APPEARANCE,
                    catcher_side=TypeSide.BRAIN,
                )
            )
            n += 1

            await self.declare_queue(
                self.progressQueue(
                    act.hid,
                    pusher_side=TypeSide.BRAIN,
                    catcher_side=TypeSide.KEEPER,
                )
            )
            n += 1
            await self.declare_queue(
                self.progressQueue(
                    act.hid,
                    pusher_side=TypeSide.BRAIN,
                    catcher_side=TypeSide.APPEARANCE,
                )
            )
            n += 1

            await self.declare_queue(
                self.resultQueue(
                    act.hid,
                    pusher_side=TypeSide.BRAIN,
                    catcher_side=TypeSide.KEEPER,
                )
            )
            n += 1
            await self.declare_queue(
                self.resultQueue(
                    act.hid,
                    pusher_side=TypeSide.BRAIN,
                    catcher_side=TypeSide.APPEARANCE,
                )
            )
            n += 1

            time.sleep(0.2)

            logger.info(f"🌱 Declared {n} queue(s) for act `{act.name['en']}`.")

        logger.info(f"🌱 Declared {len(self.acts)} act(s).")


def queue(
    type: TypeQueue,
    hid_server: str,
    pusher_side: TypeSide,
    catcher_side: TypeSide,
    hid_act: str = "",
):
    keys = [
        type.name.lower(),
        hid_act,
        pusher_side.name.lower(),
        catcher_side.name.lower(),
        hid_server,
    ]
    name = ".".join(filter(None, keys))

    return RabbitQueue(name, auto_delete=True)

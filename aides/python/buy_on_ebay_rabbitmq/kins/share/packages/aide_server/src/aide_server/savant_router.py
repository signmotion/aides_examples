from fastapi import APIRouter, routing
from faststream.rabbit import (
    ExchangeType,
    RabbitExchange,
    RabbitQueue,
    fastapi,
)
from typing import Optional
from pydantic import Field
import time
import logging

from .helpers import skip_check_route


logger = logging.getLogger("uvicorn.error")


class SavantRouter(fastapi.RabbitRouter):
    def __init__(
        self,
        connector: str,
        nickname_server: str,
        sidename_server: str,
    ):
        assert connector.strip()
        assert nickname_server.strip()
        assert sidename_server.strip()

        super().__init__(connector)

        self.nickname = nickname_server
        self.sidename = sidename_server

    nickname: str = Field(
        ...,
        title="Nickname Server",
        description="The nickname of server.",
    )

    sidename: str = Field(
        ...,
        title="Sidename Server",
        description="The sidename of server.",
    )

    def exchange(self):
        return RabbitExchange(
            "aide",
            auto_delete=True,
            type=ExchangeType.TOPIC,
        )

    def taskQueue(
        self,
        router: Optional[APIRouter] = None,
        route_name: str = "",
    ):
        return self._queueRouter(
            "query",
            include_part=False,
            router=router,
            route_name=route_name,
        )

    def progressQueue(
        self,
        router: Optional[APIRouter] = None,
        route_name: str = "",
    ):
        return self._queueRouter(
            "progress",
            include_part=False,
            router=router,
            route_name=route_name,
        )

    def resultQueue(
        self,
        router: Optional[APIRouter] = None,
        route_name: str = "",
    ):
        return self._queueRouter(
            "result",
            include_part=False,
            router=router,
            route_name=route_name,
        )

    def requestProgressQueue(self):
        return self._requestActQueue("progress")

    def requestResultQueue(self):
        return self._requestActQueue("result")

    def responseProgressQueue(self):
        return self._responseActQueue("progress")

    def responseResultQueue(self):
        return self._responseActQueue("result")

    def logQueue(
        self,
        router: Optional[APIRouter] = None,
        route_name: str = "",
    ):
        return self._queueRouter(
            "log",
            include_part=True,
            router=router or self,
            route_name=route_name,
        )

    def _queueRouter(
        self,
        name_queue: str,
        include_part: bool,
        router: Optional[APIRouter] = None,
        route_name: str = "",
    ):
        act = route_name or (router.name if hasattr(router, "name") else type(router).__name__) or ""  # type: ignore
        return self._queueAct(name_queue, act=act, include_part=include_part)

    def _requestActQueue(self, act: str):
        return self._queueAct("request", act=act, include_part=False)

    def _responseActQueue(self, act: str):
        return self._queueAct("response", act=act, include_part=False)

    def _queueAct(
        self,
        name_queue: str,
        act: str,
        include_part: bool,
    ):
        keys = [
            act,
            self.sidename.lower() if include_part else "*",
            self.nickname,
        ]

        return RabbitQueue(
            name_queue,
            auto_delete=True,
            routing_key=".".join(keys),
        )

    async def declare_exchange(self):
        declare = self.broker.declare_exchange
        ex = self.exchange()
        await declare(ex)
        logger.info(f"\tCreated exchange `{ex.name}` with type\t{ex.type.upper}.")

    async def declare_queue(self, queue: RabbitQueue):
        await self.broker.declare_queue(queue)
        logger.info(f"\tCreated queue `{queue.name}` with key\t{queue.routing_key}.")

    async def declare_service_queues(self):
        logger.info(f"Declaring service queues...")

        await self.declare_queue(self.requestProgressQueue())
        await self.declare_queue(self.requestResultQueue())
        await self.declare_queue(self.responseProgressQueue())
        await self.declare_queue(self.responseResultQueue())
        await self.declare_queue(self.logQueue())

        logger.info(f"Declared service queues.")

    async def declare_routes_queues(self):
        # TODO optimize We don't need the queues for all routes.
        for route in self.routes:
            if isinstance(route, routing.APIRoute) and not skip_check_route(route):
                logger.info(f"Declaring queues for route `{route.name}`...")

                await self.declare_queue(self.taskQueue(route_name=route.name))
                await self.declare_queue(self.progressQueue(route_name=route.name))
                await self.declare_queue(self.resultQueue(route_name=route.name))
                time.sleep(0.2)

                logger.info(f"Declared queues for route `{route.path}`.")

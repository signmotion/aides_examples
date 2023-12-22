from abc import ABC
import aio_pika
from fastapi import APIRouter
from faststream.broker.types import P_HandlerParams, T_HandlerReturn
from faststream.broker.wrapper import HandlerCallWrapper
from faststream.rabbit import RabbitQueue
from pydantic import BaseModel, Field
from typing import Any, Callable, Dict, List, Union

from .type_side import TypeSide

from ..act import Act
from ..inner_memo import InnerMemo, NoneInnerMemo
from ..savant_router import SavantRouter


CatcherReturn = Callable[
    [Callable[P_HandlerParams, T_HandlerReturn]],
    HandlerCallWrapper[
        aio_pika.IncomingMessage,
        P_HandlerParams,
        T_HandlerReturn,
    ],
]


# Functional part of server: endpoints, tasks, etc.
class Side(ABC):
    def __init__(
        self,
        router: APIRouter,
        savant_router: SavantRouter,
        acts: List[Act],
        inner_memo: InnerMemo,
    ):
        name = type(self).__name__.replace("Side", "").upper()
        self.type = TypeSide[name]

        self.router = router
        self.savant_router = savant_router
        self.acts = acts
        self.inner_memo = inner_memo

    type: TypeSide = Field(
        ...,
        title="Type",
        description="The type for side of aide. Set by class.",
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

    inner_memo: InnerMemo = Field(
        default=NoneInnerMemo(),
        title="Inner Memo",
        description="The inner memory.",
    )

    async def push(
        self,
        message: Union[BaseModel, Dict[str, Any], str],
        queue: Union[str, RabbitQueue],
    ):
        return await self.savant_router.broker.publish(
            message,
            queue=queue,
            exchange=self.savant_router.exchange(),
            # need for production
            timeout=6,
        )

    def taskCatcher(
        self,
        hid_act: str,
        pusher_side: TypeSide,
        catcher_side: TypeSide,
    ) -> CatcherReturn:
        return self.catcher(
            self.savant_router.taskQueue(
                hid_act,
                pusher_side=pusher_side,
                catcher_side=catcher_side,
            )
        )

    def progressCatcher(
        self,
        hid_act: str,
        pusher_side: TypeSide,
        catcher_side: TypeSide,
    ) -> CatcherReturn:
        return self.catcher(
            self.savant_router.progressQueue(
                hid_act,
                pusher_side=pusher_side,
                catcher_side=catcher_side,
            )
        )

    def resultCatcher(
        self,
        hid_act: str,
        pusher_side: TypeSide,
        catcher_side: TypeSide,
    ) -> CatcherReturn:
        return self.catcher(
            self.savant_router.resultQueue(
                hid_act,
                pusher_side=pusher_side,
                catcher_side=catcher_side,
            )
        )

    def requestProgressCatcher(
        self,
        pusher_side: TypeSide,
        catcher_side: TypeSide,
    ) -> CatcherReturn:
        return self.catcher(
            self.savant_router.requestProgressQueue(
                pusher_side=pusher_side,
                catcher_side=catcher_side,
            )
        )

    def responseProgressCatcher(
        self,
        pusher_side: TypeSide,
        catcher_side: TypeSide,
    ) -> CatcherReturn:
        return self.catcher(
            self.savant_router.responseProgressQueue(
                pusher_side=pusher_side,
                catcher_side=catcher_side,
            )
        )

    def requestResultCatcher(
        self,
        pusher_side: TypeSide,
        catcher_side: TypeSide,
    ) -> CatcherReturn:
        return self.catcher(
            self.savant_router.requestResultQueue(
                pusher_side=pusher_side,
                catcher_side=catcher_side,
            )
        )

    def responseResultCatcher(
        self,
        pusher_side: TypeSide,
        catcher_side: TypeSide,
    ) -> CatcherReturn:
        return self.catcher(
            self.savant_router.responseResultQueue(
                pusher_side=pusher_side,
                catcher_side=catcher_side,
            )
        )

    def catcher(self, queue: Union[str, RabbitQueue]) -> CatcherReturn:
        """
        Decorator to define a message catcher (a subscriber in the FastAPI terminology).

        Args:
            queue (Union[str, RabbitQueue]): The name of the RabbitMQ queue.
            exchange (Union[str, RabbitExchange, None], optional): The name of the RabbitMQ exchange.

        Returns:
            Callable: A decorator function for defining message catcher.
        """
        return self.savant_router.broker.subscriber(
            queue=queue,
            exchange=self.savant_router.exchange(),
        )

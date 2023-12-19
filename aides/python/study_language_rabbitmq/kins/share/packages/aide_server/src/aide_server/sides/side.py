from abc import ABC
import aio_pika
from fastapi import APIRouter
from faststream.broker.types import P_HandlerParams, T_HandlerReturn
from faststream.broker.wrapper import HandlerCallWrapper
from faststream.rabbit import RabbitExchange, RabbitQueue
from pydantic import Field
from typing import Callable, List, Union

from ..act import Act
from ..inner_memo import InnerMemo, NoneInnerMemo
from ..savant_router import SavantRouter


# Functional part of server: endpoints, tasks, etc.
class Side(ABC):
    def __init__(
        self,
        router: APIRouter,
        savant_router: SavantRouter,
        acts: List[Act],
        inner_memo: InnerMemo,
    ):
        self.name = type(self).__name__.replace("Side", "").lower()
        self.router = router
        self.savant_router = savant_router
        self.acts = acts
        self.inner_memo = inner_memo

    name: str = Field(
        ...,
        title="Name",
        description="The name for side of aide. Set by class. Lowercase.",
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

    def catcher(
        self,
        queue: Union[str, RabbitQueue],
        exchange: Union[str, RabbitExchange, None],
    ) -> Callable[
        [Callable[P_HandlerParams, T_HandlerReturn]],
        HandlerCallWrapper[aio_pika.IncomingMessage, P_HandlerParams, T_HandlerReturn],
    ]:
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
            exchange=exchange,
        )

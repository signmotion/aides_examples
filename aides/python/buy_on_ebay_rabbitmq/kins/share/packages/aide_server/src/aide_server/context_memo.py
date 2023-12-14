from pydantic import Field
from typing import TypeVar, Generic

from .log import logger
from .memo_brokers.memo_broker import MemoBroker, NoneMemoBroker


C = TypeVar("C")


class ContextMemo(Generic[C]):
    def __init__(self, context: C, broker: MemoBroker):
        self.name = type(self).__name__
        self.context = context
        self.broker = broker

    name: str = Field(
        ...,
        title="Name",
        description="The name for context memory. By analogy with `InnerMemo`.",
    )

    context: C = Field(
        default=None,
        title="Context",
        description="Structured data of this memory.",
    )

    broker: MemoBroker = Field(
        ...,
        title="Memo Broker",
        description="Broker this inner memory.",
    )

    def __str__(self):
        return self.name


class NoneContextMemo(ContextMemo):
    def __init__(self):
        super().__init__(context=None, broker=NoneMemoBroker())

        logger.info(f"🏳️‍🌈 Initialized `{self.name}`.")

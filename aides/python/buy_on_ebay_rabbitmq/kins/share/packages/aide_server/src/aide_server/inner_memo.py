from pydantic import Field
from typing import Any

from .log import logger
from .memo_brokers.memo_broker import MemoBroker, NoneMemoBroker


class InnerMemo:
    def __init__(
        self,
        broker: MemoBroker,
    ):
        self.name = type(self).__name__
        self.broker = broker

    def get(self, key: str) -> Any:
        try:
            return self.broker.get(key)
        except KeyError:
            logger.warning(f"`{self.name}`: the key `{key}` is absent.")
            return ""

    def put(self, key: str, value: Any) -> None:
        return self.broker.put(key, value)

    name: str = Field(
        ...,
        title="Name",
        description="The name for inner memory. Set by class.",
    )

    broker: MemoBroker = Field(
        ...,
        title="Memo Broker",
        description="Broker this inner memory.",
    )

    def __str__(self):
        return self.name


class NoneInnerMemo(InnerMemo):
    def __init__(self):
        super().__init__(broker=NoneMemoBroker())

        logger.info(f"🏳️‍🌈 Initialized `{self.name}`.")

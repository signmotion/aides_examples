from pydantic import Field
from typing import Any

from ..log import logger


class MemoBroker:
    def __init__(self, clear: bool = False):
        self.name = type(self).__name__
        self.clear = clear

    def get(self, key: str) -> str:
        raise Exception("Should be implemented.")

    def put(self, key: str, value: Any) -> None:
        raise Exception("Should be implemented.")

    name: str = Field(
        ...,
        title="Name",
        description="The name for memo broker. Set by class.",
    )

    def __str__(self):
        return self.name


class NoneMemoBroker(MemoBroker):
    def __init__(self):
        logger.info(f"🏳️‍🌈 Initialized `{self.name}`.")

    def get(self, key: str) -> Any:
        logger.info(f"🟡 Get value from `{self.name}`.")
        return False

    def put(self, key: str, value: Any):
        logger.info(f"🟡 Put value to `{self.name}`.")

from pydantic import Field
from typing import Any


class KeeperBroker:
    def __init__(self):
        self.name = type(self).__name__

    def get(self, key: str):
        raise Exception("Should be implemented.")

    def put(self, key: str, value: Any):
        raise Exception("Should be implemented.")

    name: str = Field(
        ...,
        title="Name",
        description="The name for side of aide. Set by class.",
    )

    def __str__(self):
        return self.name

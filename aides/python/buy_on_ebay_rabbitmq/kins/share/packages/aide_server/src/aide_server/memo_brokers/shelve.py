import os
import shelve
from pydantic import Field
import shutil
from typing import Any

from ..memo_brokers.memo_broker import MemoBroker
from ..log import logger


# Use https://docs.python.org/3/library/shelve.html
class ShelveMemoBroker(MemoBroker):
    def __init__(
        self,
        path_prefix: str,
        filename: str = "storage",
        clear: bool = False,
    ):
        assert path_prefix
        assert filename

        super().__init__(clear=clear)

        self.path_prefix = path_prefix
        self.filename = filename

        if clear and os.path.exists(self.path_prefix):
            logger.info(f"🔥 Purging the storage `{self}`...")
            shutil.rmtree(self.path_prefix)
            logger.info(f"🔥 Purged the storage `{self}`.")

        os.makedirs(self.path_prefix, exist_ok=True)

        logger.info(f"🏳️‍🌈 Initialized `{self.name}` with path `{self.path_prefix}`.")

    path_prefix: str = Field(
        ...,
        title="Path Prefix",
        description="The path to storage.",
    )

    filename: str = Field(
        ...,
        title="Filename",
        description="The filename of storage.",
    )

    @property
    def storage(self):
        return os.path.join(self.path_prefix, self.filename)

    def get(self, key: str) -> Any:
        with shelve.open(self.storage) as s:
            return s[key]

    def put(self, key: str, value: Any):
        with shelve.open(self.storage) as s:
            s[key] = value

    def __str__(self):
        return f"{self.name} : {self.storage}"

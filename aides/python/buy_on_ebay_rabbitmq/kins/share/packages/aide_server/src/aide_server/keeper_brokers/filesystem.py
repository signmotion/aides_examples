import json
import os
from pydantic import Field
from sanitize_filename import sanitize
import shutil
from typing import Any

from ..keeper_brokers.keeper_broker import KeeperBroker
from ..log import logger


class FilesystemKeeperBroker(KeeperBroker):
    def __init__(
        self,
        path_prefix: str,
        clear: bool = True,
    ):
        assert path_prefix

        super().__init__(clear=clear)

        self.path_prefix = path_prefix

        if clear:
            logger.info(f"🔥 Purging the storage `{self}`...")
            shutil.rmtree(self.path_prefix)
            logger.info(f"🔥 Purged the storage `{self}`.")

        os.makedirs(self.path_prefix, exist_ok=True)

        logger.info(f"🏳️‍🌈 Initialized `{self.name}` with path `{self.path_prefix}`.")

    path_prefix: str = Field(
        ...,
        title="Path Prefix",
        description="The path to storage into a filesystem.",
    )

    def path(self, filename: str):
        withoutExt = os.path.join(self.path_prefix, filename)
        return f"{withoutExt}.json"

    def get(self, key: str) -> Any:
        filename = sanitize(key)
        with open(self.path(filename), "r") as file:
            return file.read()

    def put(self, key: str, value: Any):
        filename = sanitize(key)
        with open(self.path(filename), "w") as file:
            json.dump(value, file)

    def __str__(self):
        return f"{self.name} : {self.path_prefix}"

import logging
from typing import List
from fastapi import APIRouter

from kins.share.packages.aide_server.src.aide_server.helpers import (
    unwrapMultilangTextList,
)

from .side import Side
from ..act import Act
from ..savant_router import SavantRouter

logger = logging.getLogger("uvicorn.error")


class AppearanceSide(Side):
    def __init__(
        self,
        router: APIRouter,
        savant_router: SavantRouter,
        acts: List[Act],
    ):
        super().__init__(
            router=router,
            savant_router=savant_router,
            acts=acts,
        )

        self.register_client_endpoints()

    def register_client_endpoints(self):
        logger.info(f"Registering client endpoint(s) for `{self.name}`...")

        for act in self.acts:
            self.register_client_endpoint(act)

        logger.info(
            f"Registering the {len(self.acts)} client endpoint(s) for `{self.name}`..."
        )

    def register_client_endpoint(self, act: Act):
        @self.router.get(
            path=act.path,
            name=act.name["en"],
            summary=act.summary["en"],
            description=act.description["en"],
            tags=unwrapMultilangTextList(act.tags, "en"),  # type: ignore
            operation_id=act.nickname,
        )
        async def endpoint():
            logger.warn(f"Call endpoint `{act.nickname}`")
            await self._publish_task(act)

        logger.info(
            f"Registered the client endpoint `{act.nickname}` for `{self.name}`."
        )

    async def _publish_task(self, act: Act):
        exchange = self.savant_router.exchange()
        queue = self.savant_router.queryQueue(act.nickname)

        message = act.nickname
        logger.warn("Publish task message")
        await self.savant_router.broker.publish(
            message,
            queue=queue,
            exchange=exchange,
            timeout=5,
        )

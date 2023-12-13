import logging
from typing import List
from fastapi import APIRouter
import uuid

from .side import Side
from ..act import Act
from ..helpers import unwrapMultilangTextList
from ..savant_router import SavantRouter
from ..task import Task

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

        logger.info(f"Initialized `{self.name}` with acts `{self.acts}`.")

    def register_client_endpoints(self):
        logger.info(f"Registering client endpoint(s) for `{self.name}`...")

        for act in self.acts:
            self.register_client_endpoint(act)

        logger.info(
            f"Registered the {len(self.acts)} client endpoint(s) for `{self.name}`."
        )

    def register_client_endpoint(self, act: Act):
        logger.info(
            f"Registering the client endpoint `{act.query_path}`"
            f" for `{self.name}` act `{act.hid}`..."
        )

        # task
        @self.router.get(
            path=act.query_path,
            name=act.name["en"],
            summary=act.summary["en"],
            description=act.description["en"],
            tags=unwrapMultilangTextList(act.tags, "en"),  # type: ignore[override]
            operation_id=act.hid,
        )
        # catcher: Brain
        async def task_endpoint():
            logger.info(f"Call endpoint `{act.query_path}` for act `{act.hid}`.")
            return await self._publish_task(act)

        # progress
        @self.router.get(
            path=act.progress_path,
            name=act.name_progress["en"],
            summary=act.summary_progress["en"],
            description=act.description_progress["en"],
            tags=unwrapMultilangTextList(act.tags_progress, "en"),  # type: ignore[override]
            operation_id=act.hid,
        )
        # catcher: Keeper
        async def request_progress_endpoint(uid_task: str):
            path = act.progress_path.replace("{uid_task}", uid_task)
            logger.info(f"Call the endpoint `{path}` for act `{act.hid}`.")
            return await self._publish_request_progress(act, uid_task)

        logger.info(
            f"Registered the client endpoints `{act.paths}`"
            f" for `{self.name}` act `{act.hid}`."
        )

    async def _publish_task(self, act: Act):
        exchange = self.savant_router.exchange()
        queue = self.savant_router.taskQueue(act.hid)
        task = Task(uid=str(uuid.uuid4()), hid_act=act.hid)

        logger.info(
            f"Publish a task `{task}` to Savant:"
            f" exchange `{exchange.name}`, queue `{queue.name}`."
        )
        await self.savant_router.broker.publish(
            task,
            queue=queue,
            exchange=exchange,
            timeout=6,
        )

        return task.uid

    async def _publish_request_progress(self, act: Act, uid_task: str):
        exchange = self.savant_router.exchange()
        queue = self.savant_router.progressQueue(act.hid)

        logger.info(
            f"Publish a request progress of task `{uid_task}` to Savant:"
            f" exchange `{exchange.name}`, queue `{queue.name}`."
        )
        await self.savant_router.broker.publish(
            uid_task,
            queue=queue,
            exchange=exchange,
            timeout=6,
        )

        return True

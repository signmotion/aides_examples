from fastapi import APIRouter
from typing import List
import uuid

from .side import Side

from ..act import Act
from ..inner_memo import InnerMemo
from ..helpers import unwrapMultilangTextList
from ..log import logger
from ..savant_router import SavantRouter
from ..task import Progress, Result, Task


class AppearanceSide(Side):
    def __init__(
        self,
        router: APIRouter,
        savant_router: SavantRouter,
        acts: List[Act],
        inner_memo: InnerMemo,
    ):
        super().__init__(
            router=router,
            savant_router=savant_router,
            acts=acts,
            inner_memo=inner_memo,
        )

        self._register_catchers_and_endpoints()

        logger.info(
            f"🏳️‍🌈 Initialized `{self.name}` with acts `{self.acts}`"
            f" and inner memo `{self.inner_memo}`."
        )

    def _register_catchers_and_endpoints(self):
        logger.info(
            f"🪶 Registering the catchers and client endpoint(s)"
            f" for `{self.name}`..."
        )

        for act in self.acts:
            self._act_register_catcher_and_endpoints(act)

        logger.info(
            f"🪶 Registered the catchers and client endpoint(s)"
            f" for `{self.name}`, {len(self.acts)} acts."
        )

    def _act_register_catcher_and_endpoints(self, act: Act):
        logger.info(
            f"🪶 Registering the catchers and endpoints for `{act.paths}`"
            f" `{self.name}` act `{act.hid}`..."
        )

        self._task_act_register_endpoint(act)

        self._request_progress_act_register_endpoint(act)
        self._response_progress_register_catcher_and_endpoint(act)

        self._request_result_act_register_endpoint(act)
        self._response_result_register_catcher_and_endpoint(act)

        logger.info(
            f"🪶 Registered the catchers and endpoints for `{act.paths}`"
            f" `{self.name}` act `{act.hid}`."
        )

    # TASK
    def _task_act_register_endpoint(self, act: Act):
        # publish task
        # catcher: Brain
        @self.router.get(
            path=act.path,
            name=act.name["en"],
            summary=act.summary["en"],
            description=act.description["en"],
            tags=unwrapMultilangTextList(act.tags, "en"),  # type: ignore[override]
            # operation_id=act.hid,
        )
        async def task_endpoint():
            logger.info(f"Call endpoint `{act.path}` for act `{act.hid}`.")
            return await self._publish_task(act)

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

    # PROGRESS
    def _request_progress_act_register_endpoint(self, act: Act):
        # request progress endpoint
        # catcher: Keeper
        @self.router.get(
            path=act.path_request_progress,
            name=act.name_request_progress["en"],
            summary=act.summary_request_progress["en"],
            description=act.description_request_progress["en"],
            tags=unwrapMultilangTextList(act.tags_request_progress, "en"),  # type: ignore[override]
            # operation_id=act.hid,
        )
        async def request_progress_endpoint(uid_task: str):
            path = act.path_request_progress.replace("{uid_task}", uid_task)
            logger.info(f"Call the endpoint `{path}`.")
            return await self._publish_request_progress(act, uid_task)

    # Returns a generated endpoint string for take a progress later.
    async def _publish_request_progress(self, act: Act, uid_task: str):
        exchange = self.savant_router.exchange()
        queue = self.savant_router.requestProgressQueue()

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

        return act.path_response_progress.replace("{uid_task}", uid_task)

    def _response_progress_register_catcher_and_endpoint(self, act: Act):
        # response progress catcher
        # memorize it to inner memory
        @self.savant_router.broker.subscriber(
            queue=self.savant_router.responseProgressQueue(),
            exchange=self.savant_router.exchange(),
        )
        async def response_progress_catcher(progress: Progress):
            logger.info(f"Catched a response progress `{progress}`.")
            if isinstance(progress, dict):
                progress = Progress.model_validate(progress)
            self._response_progress_catched(progress)

        # response progress endpoint
        # returns a progress value after call a request_progress_endpoint and
        # catch a response in response_progress_catcher
        @self.router.get(
            path=act.path_response_progress,
            name=act.name_response_progress["en"],
            summary=act.summary_response_progress["en"],
            description=act.description_response_progress["en"],
            tags=unwrapMultilangTextList(act.tags_response_progress, "en"),  # type: ignore[override]
            # operation_id=act.hid,
        )
        async def response_progress_endpoint(uid_task: str):
            path = act.path_response_progress.replace("{uid_task}", uid_task)
            logger.info(f"Call the endpoint `{path}`.")

            key = f"{uid_task}.response_progress"

            return self.inner_memo.get(key)

    def _response_progress_catched(self, progress: Progress):
        key = f"{progress.uid_task}.response_progress"
        self.inner_memo.put(key, progress.value)

    # RESULT
    def _request_result_act_register_endpoint(self, act: Act):
        # request result endpoint
        # catcher: Keeper
        @self.router.get(
            path=act.path_request_result,
            name=act.name_request_result["en"],
            summary=act.summary_request_result["en"],
            description=act.description_request_result["en"],
            tags=unwrapMultilangTextList(act.tags_request_result, "en"),  # type: ignore[override]
            # operation_id=act.hid,
        )
        async def request_result_endpoint(uid_task: str):
            path = act.path_request_result.replace("{uid_task}", uid_task)
            logger.info(f"Call the endpoint `{path}`.")
            return await self._publish_request_result(act, uid_task)

    # Returns a generated endpoint string for take a result later.
    async def _publish_request_result(self, act: Act, uid_task: str):
        exchange = self.savant_router.exchange()
        queue = self.savant_router.requestResultQueue()

        logger.info(
            f"Publish a request result of task `{uid_task}` to Savant:"
            f" exchange `{exchange.name}`, queue `{queue.name}`."
        )
        await self.savant_router.broker.publish(
            uid_task,
            queue=queue,
            exchange=exchange,
            timeout=6,
        )

        return act.path_response_result.replace("{uid_task}", uid_task)

    def _response_result_register_catcher_and_endpoint(self, act: Act):
        # response result catcher
        # memorize it to inner memory
        @self.savant_router.broker.subscriber(
            queue=self.savant_router.responseResultQueue(),
            exchange=self.savant_router.exchange(),
        )
        async def response_result_catcher(result: Result):
            logger.info(f"Catched a response result `{result}`.")
            if isinstance(result, dict):
                result = Result.model_validate(result)
            self._response_result_catched(result)

        # response result endpoint
        # returns a result value after call a request_result_endpoint and
        # catch a response in response_result_catcher
        @self.router.get(
            path=act.path_response_result,
            name=act.name_response_result["en"],
            summary=act.summary_response_result["en"],
            description=act.description_response_result["en"],
            tags=unwrapMultilangTextList(act.tags_response_result, "en"),  # type: ignore[override]
            # operation_id=act.hid,
        )
        async def response_result_endpoint(uid_task: str):
            path = act.path_response_result.replace("{uid_task}", uid_task)
            logger.info(f"Call the endpoint `{path}`.")

            key = f"{uid_task}.response_result"

            return self.inner_memo.get(key)

    def _response_result_catched(self, result: Result):
        key = f"{result.uid_task}.response_result"
        self.inner_memo.put(key, result.value)

from fastapi import APIRouter
from pydantic import Field
from typing import List
import uuid

from kins.share.packages.short_json.src.short_json.short_json import short_json

from .side import Side

from ..act import Act
from ..context_memo import ContextMemo, NoneContextMemo
from ..inner_memo import InnerMemo
from ..helpers import unwrapMultilangTextList
from ..log import logger
from ..routes import about, context
from ..savant_router import SavantRouter
from ..task import Progress, Result, Task


class AppearanceSide(Side):
    def __init__(
        self,
        router: APIRouter,
        name_aide: str,
        hid_aide: str,
        path_to_face: str,
        savant_router: SavantRouter,
        acts: List[Act],
        inner_memo: InnerMemo,
        context_memo: ContextMemo,
        catch_progress: bool = True,
        catch_result: bool = True,
    ):
        assert not isinstance(
            context_memo, NoneContextMemo
        ), "The Appearance should have a context memo."

        super().__init__(
            router=router,
            savant_router=savant_router,
            acts=acts,
            inner_memo=inner_memo,
        )

        self.context_memo = context_memo
        self.catch_progress = catch_progress
        self.catch_result = catch_result

        self._register_catchers_and_endpoints(
            name_aide=name_aide,
            hid_aide=hid_aide,
            path_to_face=path_to_face,
        )

        logger.info(
            f"🏳️‍🌈 Initialized `{self.name}` with acts `{self.acts}`"
            f" and inner memo `{self.inner_memo}`."
        )

    context_memo: ContextMemo = Field(
        ...,
        title="Context Memo",
        description="The context memory.",
    )

    catch_progress: bool = Field(
        ...,
        title="Catch Progress",
        description="Catch progress from Savant and save it to inner memory without additional request to Keeper.",
    )

    catch_result: bool = Field(
        ...,
        title="Catch Result",
        description="Catch result from Savant and save it to inner memory without additional request to Keeper.",
    )

    def _register_catchers_and_endpoints(
        self,
        name_aide: str,
        hid_aide: str,
        path_to_face: str,
    ):
        logger.info(
            f"🪶 Registering the catchers and client endpoint(s)"
            f" for `{self.name}`..."
        )

        # add about routes
        about.add_routes(
            self.router,
            name=name_aide,
            hid=hid_aide,
            sidename=self.name,
            path_to_face=path_to_face,
        )
        logger.info("🪶🍁 Added the routes for `About`.")

        # add context routes
        context.add_routes(self.router, context_memo=self.context_memo)
        logger.info("🪶🍁 Added the routes for `Context`.")

        # add acts routes
        for act in self.acts:
            self._act_register_catchers_and_endpoints(act)

        logger.info(
            f"🪶 Registered the catchers and client endpoints"
            f" for `{self.name}`, {len(self.acts)} acts."
        )

    def _act_register_catchers_and_endpoints(self, act: Act):
        logger.info(
            f"🪶 Registering the catchers and client endpoints"
            f" for `{act.paths}`"
            f" `{self.name}` act `{act.hid}`..."
        )

        n = 0

        self._task_act_register_endpoint(act)
        n += 1

        self._request_progress_act_register_endpoint(act)
        n += 1
        self._response_progress_register_catcher_and_endpoint(act)
        n += 1

        self._request_result_act_register_endpoint(act)
        n += 1
        self._response_result_register_catcher_and_endpoint(act)
        n += 1

        if self.catch_progress:

            @self.progressCatcher(act.hid)
            async def progress_catcher(progress: Progress):
                await self._catch_progress(progress)

            n += 1

        if self.catch_result:

            @self.resultCatcher(act.hid)
            async def result_catcher(result: Result):
                await self._catch_result(result)

            n += 1

        logger.info(
            f"🪶 Registered {n} catchers and endpoints"
            f" for `{act.paths}`"
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
        uid = str(uuid.uuid4())
        logger.info(f"Publish task `{uid}` with context `{self.context_memo.context}`.")
        task = Task(
            uid=uid,
            hid_act=act.hid,
            context=self.context_memo.context.dict(),
        )
        queue = self.savant_router.taskQueue(act.hid)
        logger.info(
            f"Publish a task `{short_json(task)}` to Savant:" f" queue `{queue.name}`."
        )
        await self.push(task, queue=queue)

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
        queue = self.savant_router.requestProgressQueue()
        logger.info(
            f"Publish a request progress of task `{uid_task}` to Savant:"
            f" queue `{queue.name}`."
        )
        await self.push(uid_task, queue=queue)

        return act.path_response_progress.replace("{uid_task}", uid_task)

    def _response_progress_register_catcher_and_endpoint(self, act: Act):
        # response progress catcher
        # memorize it to inner memory
        @self.responseProgressCatcher()
        async def response_progress_catcher(progress: Progress):
            await self._catch_progress(progress)

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

    async def _catch_progress(self, progress: Progress):
        logger.info(f"Catched a response progress `{progress}`.")
        if isinstance(progress, dict):
            progress = Progress.model_validate(progress)
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
        queue = self.savant_router.requestResultQueue()
        logger.info(
            f"Publish a request result of task `{uid_task}` to Savant:"
            f" queue `{queue.name}`."
        )
        await self.push(uid_task, queue=queue)

        return act.path_response_result.replace("{uid_task}", uid_task)

    def _response_result_register_catcher_and_endpoint(self, act: Act):
        # response result catcher
        # memorize it to inner memory
        @self.responseResultCatcher()
        async def response_result_catcher(result: Result):
            await self._catch_result(result)

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

    async def _catch_result(self, result: Result):
        logger.info(f"Catched a response result `{result}`.")
        if isinstance(result, dict):
            result = Result.model_validate(result)
        key = f"{result.uid_task}.response_result"
        self.inner_memo.put(key, result.value)

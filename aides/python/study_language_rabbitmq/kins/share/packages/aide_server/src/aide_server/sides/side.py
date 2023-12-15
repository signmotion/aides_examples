from abc import ABC
from fastapi import APIRouter
from pydantic import Field
from typing import List

from ..act import Act
from ..inner_memo import InnerMemo, NoneInnerMemo
from ..savant_router import SavantRouter


# Functional part of server: endpoints, tasks, etc.
class Side(ABC):
    def __init__(
        self,
        router: APIRouter,
        savant_router: SavantRouter,
        acts: List[Act],
        inner_memo: InnerMemo,
    ):
        self.name = type(self).__name__.replace("Side", "").lower()
        self.router = router
        self.savant_router = savant_router
        self.acts = acts
        self.inner_memo = inner_memo

    name: str = Field(
        ...,
        title="Name",
        description="The name for side of aide. Set by class. Lowercase.",
    )

    router: APIRouter = Field(
        ...,
        title="Router",
        description="The router for set of acts.",
    )

    savant_router: SavantRouter = Field(
        ...,
        title="Savant Router",
        description="The router of Savant.",
    )

    acts: List[Act] = Field(
        default=[],
        title="Acts Aide",
        description="Possible acts this aide.",
    )

    inner_memo: InnerMemo = Field(
        default=NoneInnerMemo(),
        title="Inner Memo",
        description="The inner memory.",
    )

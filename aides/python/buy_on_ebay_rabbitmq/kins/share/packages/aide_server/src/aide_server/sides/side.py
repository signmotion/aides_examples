import logging
from typing import List
from fastapi import APIRouter
from pydantic import Field

from ..act import Act
from ..memo import Memo, NoneMemo
from ..savant_router import SavantRouter

logger = logging.getLogger("uvicorn.error")


# Functional part of server: endpoints, tasks, etc.
class Side:
    def __init__(
        self,
        router: APIRouter,
        savant_router: SavantRouter,
        acts: List[Act],
    ):
        self.name = type(self).__name__.replace("Side", "").lower()
        self.router = router
        self.savant_router = savant_router
        self.acts = acts

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

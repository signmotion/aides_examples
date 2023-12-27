from pydantic import BaseModel, Field
from typing import Any, List
from .meaning_data import MeaningData


class Label(BaseModel):
    value: MeaningData = Field(
        ...,
        title="Value",
        description="A value for `data`.",
    )

    score: float = Field(
        ...,
        title="Score",
        description="A score for `data`.",
    )

    data: Any = Field(
        ...,
        title="Data",
        description="A data from `query` labeled with `value`.",
    )


class LabeledQuery(BaseModel):
    query: Any = Field(
        ...,
        title="Query",
        description="An original query.",
    )

    labels: List[Label] = Field(
        ...,
        title="Query",
        description="An original query.",
    )

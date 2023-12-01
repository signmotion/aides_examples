from fastapi import APIRouter, Body
from pydantic import BaseModel, Field
import json

from ..internal.config import *


router = APIRouter()


class Context(BaseModel):
    hours: int = Field(
        default=24,
        title="Text",
        description="For how many recent hours we want to see product data.",
    )
    location: str = Field(
        default="",
        title="Text",
        description="The country or city and state. E.g. Canada or San Francisco, CA.",
    )
    query: str = Field(
        default="",
        title="Text",
        description="Auction search query. E.g. smartphone.",
    )


_ctx: Context = Context()


def test_context_smarthone():
    return Context.parse_obj(
        {
            "hours": 24,
            "location": "Canada",
            "query": "smartphone",
        }
    )


if use_test_context:
    _ctx = test_context_smarthone()
    print("Initialized with the test context.")


@router.get("/context")
def context():
    return _ctx


@router.get("/schema")
def schema():
    return json.loads(Context.schema_json())


@router.get("/context/{hid}")
def value(hid: str):
    return _ctx[hid] if hid in _ctx else None


# the context's setters section
# See [schema].


@router.put("/hours")
def hours(value: int = Body(embed=True)):
    _ctx.hours = value


@router.put("/location")
def location(value: str = Body(embed=True)):
    _ctx.location = value


@router.put("/query")
def query(value: str = Body(embed=True)):
    _ctx.query = value

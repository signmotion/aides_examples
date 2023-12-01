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
    return getattr(_ctx, hid)


# See [schema].
@router.put("/context/{hid}/{value}")
def put_inline_hid_value(hid: str, value: str):
    setattr(_ctx, hid, value)
    return True


# See [schema].
@router.put("/context/{hid}")
def put_inline_hid_json_value(
    hid: str,
    value: str = Body(embed=True),
):
    setattr(_ctx, hid, value)
    return True


# See [schema].
@router.put("/context")
def put_json_hid_value(
    hid: str = Body(embed=True),
    value: str = Body(embed=True),
):
    setattr(_ctx, hid, value)
    return True

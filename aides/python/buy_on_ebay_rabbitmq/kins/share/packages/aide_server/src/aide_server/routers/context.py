import json
from fastapi import APIRouter, Body
from ..memo import Memo


def router(memo: Memo):
    api = APIRouter()

    @api.get("/schema")
    def schema():
        return json.loads(memo.context.schema_json())

    @api.get("/get-context")
    def get_context():
        return memo.context

    @api.get("/get-context-value/{hid}")
    def get_context_value(hid: str):
        return getattr(memo.context, hid)

    # See [schema].
    @api.put("/set-context-value")
    def set_context_value(
        hid: str = Body(
            embed=True,
            title="HID",
            description="ID for human perception.",
        ),
        value: str = Body(
            embed=True,
            title="Value",
            description="Value for set by HID.",
        ),
    ):
        setattr(memo.context, hid, value)
        return True

    return api

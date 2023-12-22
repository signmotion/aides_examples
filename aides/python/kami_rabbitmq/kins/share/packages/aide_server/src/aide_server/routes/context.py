from fastapi import APIRouter, Body
import json

from ..context_memo import ContextMemo


def add_routes(router: APIRouter, context_memo: ContextMemo):
    @router.get("/schema")
    def schema():
        return json.loads(context_memo.context.schema_json())

    @router.get(
        "/get-context",
        operation_id="get_context",
    )
    def get_context():
        return context_memo.context

    @router.get(
        "/get-context-value/{hid}",
        operation_id="get_context_value",
    )
    def get_context_value(hid: str):
        return getattr(context_memo.context, hid)

    # See [schema].
    @router.put(
        "/set-context-value",
        operation_id="set_context_value",
    )
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
        setattr(context_memo.context, hid, value)
        return True

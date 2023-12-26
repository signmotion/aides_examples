import unittest

from typing import Any, Dict
from pydantic import BaseModel, Field

from ..src.short_json.short_json import short_json


class TestContext(unittest.TestCase):
    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName=methodName)
        self.maxDiff = None

    def test_short_json_pydantic(self):
        expected = {
            "uid": "ae46dbdd-a9f8-4a80-8e27-985572ffb0bc",
            "hid_act": "translate_caption",
            "context": {
                "languages": {"target": "uk"},
                "text": """
1
00:05:46,388 --> 00:05:47,430
Abs, you ready?

2
00:05:47,472 --> 00:05:49,474
Abby...

3
00:05:52,727 --> 00:05:54,5...""",
            },
            "list_value": [1, 2, 3, 4, "..."],
            "set_value": {1, 2, 3, 4, "..."},
            "map_value": {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6},
        }
        shorted = short_json(a, slice_str_to_length=48)
        self.assertEqual(expected, shorted)


class A(BaseModel):
    uid: str = Field(
        ...,
        title="UID",
        description="UID of task. We can access to the task known only this UID.",
    )

    hid_act: str = Field(
        ...,
        title="HID Act",
        description="Nick name of act aide.",
    )

    context: Dict[str, Any] = Field(
        default={},
        title="Context Act",
        description="Context as key-value of act aide. Can be declared as concrete class for acts.",
    )

    list_value: list
    set_value: set
    map_value: dict


text = """
1
00:05:46,388 --> 00:05:47,430
Abs, you ready?

2
00:05:47,472 --> 00:05:49,474
Abby...

3
00:05:52,727 --> 00:05:54,521
Abs.

4
00:05:58,066 --> 00:06:00,402
Come on. I know you're in there.
Let's go.

5
00:06:01,695 --> 00:06:03,238
Abby, come on.

6
00:06:03,279 --> 00:06:05,532
Okay, okay.

7
00:06:06,616 --> 00:06:07,826
You're being a jerk.

"""

a = A(
    uid="ae46dbdd-a9f8-4a80-8e27-985572ffb0bc",
    hid_act="translate_caption",
    context={
        "languages": {"target": "uk"},
        "text": text,
    },
    list_value=[1, 2, 3, 4, 5, 6, 7, 8],
    set_value={1, 2, 3, 4, 5, 6, 7, 8},
    map_value={"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6},
)

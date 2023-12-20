from pydantic import BaseModel, Field, NonNegativeFloat
from typing import Any, Dict


class Task(BaseModel):
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

    def __str__(self):
        return f"{self.uid} : {self.hid_act} : {self.context}"


class Progress(BaseModel):
    uid_task: str = Field(
        ...,
        title="UID Task",
        description="UID of task for this progress value.",
    )

    value: NonNegativeFloat = Field(
        ...,
        title="Value",
        description="Value of task progress. Range: [0.0; 100.0].",
    )

    def __str__(self):
        return f"{self.uid_task} : {self.value} %"


class Result(BaseModel):
    uid_task: str = Field(
        ...,
        title="UID Task",
        description="UID of task for this result value.",
    )

    value: Any = Field(
        ...,
        title="Value",
        description="Result of task.",
    )

    def __str__(self):
        return f"{self.uid_task} : {self.value}"

from pydantic import BaseModel, Field


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

    def __str__(self):
        return f"{self.uid}:{self.hid_act}"

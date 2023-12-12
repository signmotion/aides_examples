from pydantic import BaseModel, Field


class Task(BaseModel):
    uid: str = Field(
        ...,
        title="UID",
        description="UID of task. We can access to the task known only this UID.",
    )

    nickname_act: str = Field(
        ...,
        title="Nickname Act",
        description="Nick name of act aide.",
    )

    def __str__(self):
        return f"{self.uid}:{self.nickname_act}"

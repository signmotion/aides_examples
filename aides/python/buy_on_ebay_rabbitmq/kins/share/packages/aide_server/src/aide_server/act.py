from typing import Dict, List
from pydantic import BaseModel, Field


class Act(BaseModel):
    name: Dict[str, str] = Field(
        ...,
        title="Name",
        description="Name of act aide.",
    )

    hid: str = Field(
        ...,
        title="HID",
        description="Nick name of act aide.",
    )

    @property
    def path(self):
        return f"/{self.hid.replace('_', '-')}"

    summary: Dict[str, str] = Field(
        default={},
        title="Summary",
        description="Summary of act aide.",
    )

    description: Dict[str, str] = Field(
        default={},
        title="Description",
        description="Description of act aide.",
    )

    tags: List[Dict[str, str]] = Field(
        default=[],
        title="Tags",
        description="Tags for act aide.",
    )

    version: str = Field(
        default="0.1.0",
        title="Version",
        description="Version of act aide.",
    )

    # def __call__(self, memo: Memo):
    #    raise Exception("Should be released into Brain.")

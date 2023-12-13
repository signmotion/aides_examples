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
    def query_path(self):
        return f"/{self.hid.replace('_', '-')}"

    @property
    def progress_path(self):
        return f"{self.query_path}/progress/" "{uid_task}"

    @property
    def result_path(self):
        return f"{self.query_path}/result"

    @property
    def paths(self):
        return [self.query_path, self.progress_path, self.result_path]

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

    @property
    def name_progress(self):
        return {"en": f"Progress of {self.name['en']}"}

    @property
    def summary_progress(self):
        return {"en": f"Progress value for {self.name['en']}."}

    @property
    def description_progress(self):
        return {
            "en": f"Percentage progress for {self.name['en']}. Range: [0.0; 100.0]."
        }

    @property
    def tags_progress(self):
        return self.tags + [{"en": "progress"}]

    version: str = Field(
        default="0.1.0",
        title="Version",
        description="Version of act aide.",
    )

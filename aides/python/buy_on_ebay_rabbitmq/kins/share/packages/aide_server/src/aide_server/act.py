from pydantic import BaseModel, Field
from typing import Dict, List


class Act(BaseModel):
    hid: str = Field(
        ...,
        title="HID",
        description="Nick name of act aide.",
    )

    @property
    def path_request_result(self):
        return f"{self.path}/request-result" "{uid_task}"

    @property
    def paths(self):
        return [self.path, self.path_request_progress, self.path_request_result]

    # call act (send task to Brain)
    @property
    def path(self):
        """
        Endpoint to call this act.
        """
        return f"/{self.hid.replace('_', '-')}"

    name: Dict[str, str] = Field(
        ...,
        title="Name",
        description="Name of act aide.",
    )

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

    # request progress (send request to Keeper)
    @property
    def path_request_progress(self):
        return f"{self.path}/request-progress/" "{uid_task}"

    @property
    def name_request_progress(self):
        return {"en": f"Request progress for {self.name['en']}"}

    @property
    def summary_request_progress(self):
        return {"en": f"Request progress value for {self.name['en']}."}

    @property
    def description_request_progress(self):
        return {
            "en": f"Request progress in percentage for {self.name['en']}. Range: [0.0; 100.0]."
        }

    @property
    def tags_request_progress(self):
        return self.tags + [{"en": "progress"}, {"en": "request"}]

    # response progress (get requested progress from appearance memory)
    @property
    def path_response_progress(self):
        return f"{self.path}/response-progress/" "{uid_task}"

    @property
    def name_response_progress(self):
        return {"en": f"Response progress for {self.name['en']}"}

    @property
    def summary_response_progress(self):
        return {"en": f"Response progress value for {self.name['en']}."}

    @property
    def description_response_progress(self):
        return {
            "en": f"Response progress in percentage for {self.name['en']}. Range: [0.0; 100.0]."
        }

    @property
    def tags_response_progress(self):
        return self.tags + [{"en": "progress"}, {"en": "response"}]

    version: str = Field(
        default="0.1.0",
        title="Version",
        description="Version of act aide.",
    )

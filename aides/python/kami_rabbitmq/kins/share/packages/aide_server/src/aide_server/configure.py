from pydantic import BaseModel, Field
from typing import Dict, List, Optional

from .act import Act
from .characteristic import Characteristic


class Configure(BaseModel):
    name: Dict[str, str] = Field(
        ...,
        title="Name",
        description="Name of aide.",
    )

    hid: str = Field(
        ...,
        title="HID",
        description="Nick name of aide.",
    )

    summary: Dict[str, str] = Field(
        default={},
        title="Summary",
        description="Summary of aide.",
    )

    description: Dict[str, str] = Field(
        default={},
        title="Description",
        description="Description of aide.",
    )

    tags: List[Dict[str, str]] = Field(
        default=[],
        title="Tags",
        description="Tags for aide.",
    )

    path_to_face: str = Field(
        default="",
        title="HID",
        description="Nick name of aide.",
    )

    characteristic: Optional[Characteristic] = Field(
        default=None,
        title="Characteristic",
        description="Characteristic of aide.",
    )

    savant_connector: str = Field(
        ...,
        examples=["amqp://guest:guest@localhost:5672/"],
        title="Savant Connector",
        description="Connector to Savant server.",
    )

    acts: List[Act] = Field(
        default=[],
        title="Acts Aide",
        description="Possible acts this aide.",
    )

    version: str = Field(
        default="0.1.0",
        title="Version",
        description="Version of aide.",
    )

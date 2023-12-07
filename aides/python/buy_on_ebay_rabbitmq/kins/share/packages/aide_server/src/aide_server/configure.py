from typing import Dict, List, Optional
from pydantic import BaseModel, Field, PositiveInt
from .characteristic import Characteristic


class Configure(BaseModel):
    name: Optional[Dict[str, str]] = Field(
        ...,
        title="Name",
        description="Name of aide.",
    )
    nickname: str = Field(
        ...,
        title="Nickname",
        description="Nick name of aide.",
    )
    summary: Optional[Dict[str, str]] = Field(
        default=None,
        title="Summary",
        description="Summary of aide.",
    )
    description: Optional[Dict[str, str]] = Field(
        default=None,
        title="Description",
        description="Description of aide.",
    )
    tags: List[Dict[str, str]] = Field(
        default=[],
        title="Tags",
        description="Tags for aide.",
    )
    characteristic: Optional[Characteristic] = Field(
        default=None,
        title="Characteristic",
        description="Characteristic of aide.",
    )
    version: str = Field(
        default="0.1.0",
        title="Version",
        description="Version of aide.",
    )

    savantConnector: str = Field(
        ...,
        examples=["amqp://guest:guest@localhost:5672/"],
        title="Savant Connector",
        description="Connector to Savant server.",
    )

from typing import Dict
from pydantic import BaseModel, Field, PositiveInt


class Characteristic(BaseModel):
    age: PositiveInt = Field(
        default=12,
        title="Age",
        description="Age of aide.",
    )
    constitution: Dict[str, str] = Field(
        default={},
        title="Constitution",
        description="Constitution of aide: posture, build, etc.",
    )
    clothing: Dict[str, str] = Field(
        default={},
        title="Clothing",
        description="Clothing of aide: business casual attire, essential accessories, etc.",
    )
    clothing: Dict[str, str] = Field(
        default={},
        title="Clothing",
        description="Clothing of aide: business casual attire, essential accessories, etc.",
    )
    traits: Dict[str, str] = Field(
        default={},
        title="Traits",
        description="Traits of aide: analytical, decisive, detail-oriented, patient, knowledgeable, etc.",
    )

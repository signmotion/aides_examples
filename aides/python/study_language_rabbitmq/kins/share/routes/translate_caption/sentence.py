from pydantic import BaseModel, Field
from typing import Any, Dict


class Sentence(BaseModel):
    # whole sentence (value) on the language (key)
    text: Dict[str, str] = Field(default={})
    # node start (key) and count of chunks this harvested sentence in the node (value)
    chunks: Dict[str, int] = Field(default={})

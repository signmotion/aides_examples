from pydantic import BaseModel, Field
from typing import Any, Dict, List


class ValueSlice(BaseModel):
    """
    Keeps a position of query into `Context` and recognized value from query.
    """

    i: int = Field(
        ...,
        title="Query Index",
        description="A position of query into `Contex.queries`.",
    )

    v: Any = Field(
        ...,
        title="Recognized Value",
        description="A recognized value from the query by the `index` into `Context`.",
    )


class Slice(BaseModel):
    """
    Recognized data or meaning data.

    We can work with this class like with dict where a key has a name from `MeaningData`.
    """

    def __getitem__(self, key: str) -> List[ValueSlice]:
        if key not in self.raw:
            self.raw[key] = []
        return self.raw[key]

    def __setitem__(self, key: str, value: List[ValueSlice]):
        self.raw[key] = value

    def __delitem__(self, key: str):
        if key in self.raw:
            del self.raw[key]

    def has(self, key: str) -> bool:
        return hasattr(self.raw, key)

    def sort(self):
        """Sort by key."""
        self.raw = dict(sorted(self.raw.items()))

    raw: Dict[str, List[ValueSlice]] = Field(
        default={},
        title="Raw Data",
        description="Raw data presented as a map and value as a list. The list needed for keep an index of query for `slice`.",
    )

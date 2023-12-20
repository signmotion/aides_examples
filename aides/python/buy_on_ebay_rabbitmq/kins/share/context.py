from pydantic import BaseModel, Field


class Context(BaseModel):
    hours: int = Field(
        default=24,
        title="Text",
        description="For how many recent hours we want to see product data.",
    )
    location: str = Field(
        default="",
        title="Text",
        description="The country or city and state. E.g. Canada or San Francisco, CA.",
    )
    query: str = Field(
        default="",
        title="Text",
        description="Auction search query. E.g. smartphone.",
    )


def test_context_smarthone_init():
    return Context.model_validate(
        {
            "hours": 24,
            "location": "Canada",
            "query": "smartphone",
        }
    )

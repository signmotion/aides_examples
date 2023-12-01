from .internal.context import Context, test_context_smarthone
from .internal.config import use_test_context
from .routers import about, products_today

from .packages.aide_server.src.aide_server.server import (
    AideServer,
    Memo,
)

# ! See conventions in ../README.md.


app = AideServer(
    title="Auction eBay Aide",
    summary="The aide for work with the eBay's auction.",
    description="Appraise purchases items from eBay's auction.",
    version="0.1.1",
    tags=["auction", "eBay"],
    characteristic={
        "age": 19,
        # link to face: http://127.0.0.1:8000/face
        "face": "/face",
        "constitution": {
            "Posture": "Upright and alert, demonstrating attentiveness.",
            "Build": "Average, portraying approachability and practicality.",
        },
        "clothing": {
            "Business casual attire": "A blend of professionalism and comfort.",
            "Essential accessories": "A wristwatch for timekeeping and possibly glasses for detailed examination of items.",
        },
        "traits": {
            "Analytical": "Able to assess value and condition efficiently.",
            "Decisive": "Confident in making quick purchase decisions.",
            "Detail-Oriented": "Attentive to the specifics and potential flaws of items.",
            "Patient": "Willing to wait for the right item and the right price.",
            "Knowledgeable": "Well-versed in market trends and product values.",
        },
    },
    external_routers=[about.router, products_today.router],
    memo=Memo(test_context_smarthone() if use_test_context else Context()),
)


# the context section
# See `internal/context.py` and [memo] in [AideServer].


# the aide about section
# See `routers/about.py`.


# the abilities section
# See `routers/*.py`.

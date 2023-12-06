from .share.context import Context, test_context_smarthone
from .share.config import use_test_context
from .share.packages.aide_server.src.aide_server.server import AideServer, Memo
from .routers import about, products_today


_app = AideServer(
    title="Auction eBay Aide",
    summary="The aide for work with the eBay's auction.",
    description="Appraise purchases items from eBay's auction.",
    nickname="auction-ebay",
    version="0.1.1",
    tags=["auction", "buy", "eBay", "purchase"],
    characteristic={
        "age": 19,
        # link to face: http://127.0.0.1:8000/face
        # see `routers/about.py` how to declare that
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


def app():
    return _app


# the aide about section
# See `routers/about.py`.


# the abilities section
# See `routers/*.py`.

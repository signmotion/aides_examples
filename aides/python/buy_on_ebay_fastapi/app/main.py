from app.dependencies import *
from .routers import about, context, products_today

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
)

app.include_router(about.router)
app.include_router(context.router)
app.include_router(products_today.router)


# the aide character section
# See `routers/about.py`.


# the context section
# See `routers/context.py`.


# the abilities section
# See `routers/*.py`.

# !) call this functions after adding all your path operations
check_routes(app)
use_route_names_as_operation_ids(app)

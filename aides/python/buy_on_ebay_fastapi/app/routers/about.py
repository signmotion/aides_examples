from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter()


# the aide character


@router.get("/about")
def about():
    return "The aide for work with the eBay's auction."


@router.get("/tags")
# Tags for detect this aide.
# There is no need to repeat the tags below for your own functions.
def tags():
    return ["auction", "eBay"]


@router.get("/characteristic/age")
def characteristic_age():
    return 19


@router.get("/characteristic/face")
def characteristic_face():
    return FileResponse("app/data/face.webp")


@router.get("/characteristic/constitution")
def characteristic_constitution():
    return {
        "Posture": "Upright and alert, demonstrating attentiveness.",
        "Build": "Average, portraying approachability and practicality.",
    }


@router.get("/characteristic/clothing")
def characteristic_clothing():
    return {
        "Business casual attire": "A blend of professionalism and comfort.",
        "Essential accessories": "A wristwatch for timekeeping and possibly glasses for detailed examination of items.",
    }


@router.get("/characteristic/traits")
def characteristic_traits():
    return {
        "Analytical": "Able to assess value and condition efficiently.",
        "Decisive": "Confident in making quick purchase decisions.",
        "Detail-Oriented": "Attentive to the specifics and potential flaws of items.",
        "Patient": "Willing to wait for the right item and the right price.",
        "Knowledgeable": "Well-versed in market trends and product values.",
    }


@router.get("/")
def root():
    return root_about()

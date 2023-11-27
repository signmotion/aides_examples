from fastapi import APIRouter

router = APIRouter()


@router.get("/about")
def root_about():
    return "The aide for studying language."


@router.get("/tags")
def tags():
    return [
        "english",
        "language",
        "learning",
        "study",
        "teach",
        "ukrainian",
    ]


@router.get("/")
def root():
    return root_about()

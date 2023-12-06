from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter()


# the aide character

# See all characteristics when Aide instantiating into `main.py`.


@router.get("/face", include_in_schema=False)
def face():
    return FileResponse("app/appearance/data/face.webp")

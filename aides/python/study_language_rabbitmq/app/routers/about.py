from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter()


# the aide character

# See all characteristics when FastAPI instantiating.


@router.get("/face", include_in_schema=False)
def face():
    return FileResponse("app/data/face.webp")

from fastapi import APIRouter
from fastapi.responses import FileResponse


def router():
    r = APIRouter()

    @r.get("/face", include_in_schema=False)
    def face():
        return FileResponse("app/data/face.webp")

    return r

from fastapi import APIRouter
from fastapi.responses import FileResponse


def router(
    name: str,
    nickname: str,
    part: str,
    path_to_face: str,
):
    r = APIRouter()

    @r.get("/")
    def root():
        return {
            "name": name,
            "nickname": nickname,
            "part": part,
        }

    if path_to_face:

        @r.get("/face", include_in_schema=False)
        def face():
            return FileResponse(path_to_face)

    return r

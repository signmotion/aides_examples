from fastapi import APIRouter
from fastapi.responses import FileResponse


def router(
    name: str,
    nickname: str,
    sidename: str,
    path_to_face: str,
):
    api = APIRouter()

    @api.get("/")
    def root():
        return {
            "name": name,
            "nickname": nickname,
            "sidename": sidename,
        }

    if path_to_face:

        @api.get("/face", include_in_schema=False)
        def face():
            return FileResponse(path_to_face)

    return api


# You can declare any public info about Aide.
# For example, how to declare an image of aide's place that
# accesed from `http://127.0.0.1:8000/place`:
#
# from fastapi import APIRouter
#
# def router():
#     r = APIRouter()
#
#     @r.get("/place", include_in_schema=False)
#     def place():
#         return FileResponse("app/data/place.webp")
#
#     return r

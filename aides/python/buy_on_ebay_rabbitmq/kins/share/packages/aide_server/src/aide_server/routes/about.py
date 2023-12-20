from fastapi import APIRouter
from fastapi.responses import FileResponse


def add_routes(
    router: APIRouter,
    name: str,
    hid: str,
    sidename: str,
    path_to_face: str,
):
    @router.get(
        "/",
        operation_id="root",
    )
    def root():
        return {
            "name": name,
            "hid": hid,
            "sidename": sidename,
        }

    if path_to_face:

        @router.get("/face", include_in_schema=False)
        def face():
            return FileResponse(path_to_face)


# You can declare any public info about Aide.
# For example, how to declare an image of aide's place that
# accesed from `http://127.0.0.1:8000/place`:
#
# from fastapi import APIRouter
#
# def include_routes(router: APIRouter):
#     @r.get("/place", include_in_schema=False)
#     def place():
#         return FileResponse("app/data/place.webp")
#
#     return r

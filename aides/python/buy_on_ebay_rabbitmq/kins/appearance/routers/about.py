from fastapi import APIRouter


# You can declare any public info about Aide.
# For example, how to declare an image of aide's place that
# accesed from `http://127.0.0.1:8000/place`:
#
# def router():
#     r = APIRouter()
#
#     @r.get("/place", include_in_schema=False)
#     def place():
#         return FileResponse("app/data/place.webp")
#
#     return r


def router():
    return APIRouter()

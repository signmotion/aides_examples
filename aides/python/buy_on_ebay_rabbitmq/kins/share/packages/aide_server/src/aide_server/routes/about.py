from fastapi import APIRouter
from fastapi.responses import FileResponse

from ..configure import Configure


def add_routes(
    router: APIRouter,
    configure: Configure,
    sidename: str,
):
    @router.get("/", operation_id="root", include_in_schema=False)
    def root():
        return {
            "name": configure.name,
            "hid": configure.hid,
            "sidename": sidename,
        }

    @router.get("/acts", include_in_schema=False)
    def acts():
        return acts_lang("en")

    @router.get("/acts/{lang}", include_in_schema=False)
    def acts_lang(lang: str):
        return [act.unwrapped_multilang_texts(lang) for act in configure.acts]

    @router.get("/brief-acts", include_in_schema=False)
    def brief_acts():
        return brief_acts_lang("en")

    @router.get("/brief-acts/{lang}", include_in_schema=False)
    def brief_acts_lang(lang: str):
        return [act.brief_unwrapped_multilang_texts(lang) for act in configure.acts]

    if configure.path_to_face:

        @router.get("/face", include_in_schema=False)
        def face():
            return FileResponse(configure.path_to_face)


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

from kins.appearance.server import Appearance


async def appearance():
    server = Appearance()
    return await server.fastapi_app()

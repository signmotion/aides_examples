from fastapi import Depends, FastAPI
from typing_extensions import Annotated

from faststream.rabbit import RabbitBroker, fastapi

router = fastapi.RabbitRouter("amqp://guest:guest@localhost:5672/")

_app = FastAPI(lifespan=router.lifespan_context)


def app():
    return _app


@router.after_startup
async def test(app: FastAPI):
    print(f"FastStream started.\n\tFastAPI server: {app.title}")


def broker():
    return router.broker


@router.get("/hello-rabbit")
async def hello_rabbit(
    broker: Annotated[RabbitBroker, Depends(broker)],
):
    message = "Hello, Rabbit!"
    await broker.publish(message, "test")

    return f"Sent message `{message}` from HTTP."


app().include_router(router)

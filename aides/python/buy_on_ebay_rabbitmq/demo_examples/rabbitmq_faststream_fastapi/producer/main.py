from fastapi import Depends, FastAPI
from typing_extensions import Annotated
from faststream.rabbit import (
    RabbitBroker,
    ExchangeType,
    RabbitExchange,
    RabbitQueue,
    fastapi,
)


router = fastapi.RabbitRouter("amqp://guest:guest@localhost:5672/")
_app = FastAPI(lifespan=router.lifespan_context)


def app():
    return _app


@router.after_startup
async def test(app: FastAPI):
    print(f"FastStream Producer router started.\n\tFastAPI server: {app.title}")


def broker():
    return router.broker


exch = RabbitExchange("exchange", auto_delete=True, type=ExchangeType.TOPIC)
queue_1 = RabbitQueue("test-queue-1", auto_delete=True, routing_key="*.info")


publisher = router.publisher("response-q")


@publisher
@router.get("/hello-rabbit")
async def hello_rabbit(
    broker: Annotated[RabbitBroker, Depends(broker)],
):
    message = "Hello, Rabbit!"
    print(message)
    await broker.publish(
        message,
        queue=queue_1,
        routing_key="logs.info",
        exchange=exch,
        timeout=5,
    )

    return f"Sent message `{message}` from HTTP."


app().include_router(router)

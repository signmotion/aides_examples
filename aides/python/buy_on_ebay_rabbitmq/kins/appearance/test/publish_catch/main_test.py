from fastapi import Depends, FastAPI
from typing_extensions import Annotated
from faststream import Logger
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


exchange = RabbitExchange("aide", auto_delete=True, type=ExchangeType.HEADERS)

queue = RabbitQueue(
    "somename",
    auto_delete=True,
    bind_arguments={
        "act": "test",
        "nickname": "a",
    },
)


@router.after_startup
async def test(app: FastAPI):
    await bro().declare_exchange(exchange)
    await bro().declare_queue(queue)

    print(f"FastStream Test router started.\n\tFastAPI server: `{app.title}`.")


def bro():
    return router.broker


broker = RabbitBroker("amqp://guest:guest@localhost:5672/")


# publisher = router.publisher("response-q")


@broker.publisher(queue, exchange)
@router.get("/hello-test")
async def hello_test(
    broker: Annotated[RabbitBroker, Depends(bro)],
):
    print(exchange)
    print(queue)

    message = "Hello!"
    print(message)
    await broker.publish(
        message,
        exchange=exchange,
        queue=queue,
        timeout=5,
    )

    return f"Sent message `{message}` from HTTP."


@broker.subscriber(queue, exchange)
async def queue_handler(message: str, logger: Logger):
    logger.info(f"queue_handler(), message `{message}`")


app().include_router(router)

# !) Doesn't work [queue_handler].

import logging
from fastapi import Depends, FastAPI
from typing_extensions import Annotated
from faststream.rabbit import (
    RabbitBroker,
    ExchangeType,
    RabbitExchange,
    RabbitQueue,
    fastapi,
)

logger = logging.getLogger("uvicorn.error")

router = fastapi.RabbitRouter("amqp://guest:guest@localhost:5672/")
_app = FastAPI(lifespan=router.lifespan_context)


def app():
    return _app


exchange = RabbitExchange("aide_headers", auto_delete=True, type=ExchangeType.HEADERS)

queue = RabbitQueue(
    "somename_headers",
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

    logger.info(f"FastStream Test router started.\n\tFastAPI server: `{app.title}`.")


def bro():
    return router.broker


# publisher = router.publisher("response-q")


@router.broker.publisher(queue, exchange)
@router.get("/hello-test")
async def hello_test(
    broker: Annotated[RabbitBroker, Depends(bro)],
):
    logger.info(exchange)
    logger.info(queue)

    message = "Hello!"
    logger.info(message)
    await broker.publish(
        message,
        exchange=exchange,
        queue=queue,
        timeout=5,
    )

    return f"Sent message `{message}` from HTTP."


@router.broker.subscriber(queue, exchange)
async def queue_handler(message: str):
    logger.warn(f"RECEIVED! queue_handler(), message `{message}`")


app().include_router(router)

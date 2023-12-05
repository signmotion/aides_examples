from faststream import FastStream
from faststream.rabbit import RabbitBroker
from pydantic import BaseModel, Field, PositiveInt

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

_app = FastStream(broker)


def app():
    return _app


class User(BaseModel):
    user: str = Field(..., examples=["John"])
    user_id: PositiveInt = Field(..., examples=["1"])


# @broker.subscriber("in")
# @broker.publisher("out")
# async def handle_user_msg(data: User) -> str:
#    return f"User: {data.user} - {data.user_id} registered"


@broker.subscriber("test")
# @broker.publisher("test")
async def handle_hello_rabbit_msg(message: str) -> str:
    return f"Message: `{message}` received."

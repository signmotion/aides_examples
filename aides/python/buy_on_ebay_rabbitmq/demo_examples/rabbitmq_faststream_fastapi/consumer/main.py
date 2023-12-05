from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker, ExchangeType, RabbitExchange, RabbitQueue

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = FastStream(broker)


exchange = RabbitExchange("exchange", auto_delete=True, type=ExchangeType.TOPIC)
queue_1 = RabbitQueue("test-queue-1", auto_delete=True, routing_key="*.info")


@broker.subscriber(queue_1, exchange)
async def base_handler1(msg: str, logger: Logger):
    logger.info(f"handler queue_1, msg `{msg}`")


# class User(BaseModel):
#     user: str = Field(..., examples=["John"])
#     user_id: PositiveInt = Field(..., examples=["1"])


# @broker.subscriber("in")
# @broker.publisher("out")
# async def handle_user_msg(data: User) -> str:
#    return f"User: {data.user} - {data.user_id} registered"


# @broker.subscriber("in")
# @broker.publisher("out")
# async def handle_hello_rabbit_msg(message: str) -> str:
#     logger.info("Received message: %s", message)

#     return f"Message: `{message}` received."

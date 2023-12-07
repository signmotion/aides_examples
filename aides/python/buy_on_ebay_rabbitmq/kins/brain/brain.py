from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker, ExchangeType, RabbitExchange, RabbitQueue

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = FastStream(broker)


exchange = RabbitExchange("aide", auto_delete=True, type=ExchangeType.HEADERS)

queue_query = RabbitQueue(
    "query",
    auto_delete=True,
    bind_arguments={"act": "products-today", "nickname": "auction-ebay"},
)


@broker.subscriber(queue_query, exchange)
async def queue_query_handler(context: dict, logger: Logger):
    logger.info(f"queue_query_handler(), context `{context}`")

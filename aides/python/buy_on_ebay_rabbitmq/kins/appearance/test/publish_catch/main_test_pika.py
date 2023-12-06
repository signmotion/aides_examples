import pika

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()

channel.exchange_declare(exchange="headers_exchange", exchange_type="headers")

channel.queue_declare(queue="my_queue")
channel.queue_bind(
    exchange="headers_exchange",
    queue="my_queue",
    arguments={
        "x-match": "all",
        "header1": "value1",
        "header2": "value2",
    },
)

message = "Hello, headers exchange!"
properties = pika.BasicProperties(headers={"header1": "value1", "header2": "value2"})
channel.basic_publish(
    exchange="headers_exchange", routing_key="", body=message, properties=properties
)

connection.close()

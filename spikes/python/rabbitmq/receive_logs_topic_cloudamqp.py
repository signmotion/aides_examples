# consumer
from dotenv import load_dotenv
import os, pika, sys

# Source: https://cloudamqp.com/docs/python.html

load_dotenv()

url = os.environ.get("CLOUDAMQP_URL", "amqp://guest:guest@localhost:5672/%2f")
params = pika.ConnectionParameters(host="localhost")
params.socket_timeout = 5
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.exchange_declare(exchange="topic_logs", exchange_type="topic")

result = channel.queue_declare("", exclusive=True)
queue_name = result.method.queue
print(f"queue_name `{queue_name}`")

binding_keys = sys.argv[1:]
if not binding_keys:
    sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
    sys.exit(1)

for binding_key in binding_keys:
    channel.queue_bind(
        exchange="topic_logs",
        queue=queue_name,
        routing_key=binding_key,
    )

print(f"[*] Waiting for logs. {url}\nTo exit press CTRL+C")


def callback(ch, method, properties, body):
    print(f"[x] {method.routing_key}:{body}")


channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True,
)

channel.start_consuming()

connection.close()

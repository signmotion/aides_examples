# producer
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

routing_key = sys.argv[1] if len(sys.argv) > 2 else "anonymous.info"
message = " ".join(sys.argv[2:]) or "Hello World!"
channel.basic_publish(
    exchange="topic_logs",
    routing_key=routing_key,
    body=message,
)
print(f"[x] Sent `{routing_key}:{message}` to {url}")

connection.close()

import pika, time

# python worker.py

connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()

channel.queue_declare(queue="task_queue", durable=True)
print("[*] Waiting for messages. To exit press CTRL+C")


def callback(ch, method, properties, body):
    count = body.count(b".")
    print(f"[x] Received `{body.decode()}` with weight {count}.")

    time.sleep(count)

    print("[x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(
    queue="task_queue",
    on_message_callback=callback,
)

channel.start_consuming()

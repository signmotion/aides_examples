from celery import Celery
from fastapi import FastAPI

app = FastAPI()

# TIMEZONE = "US/Eastern"

celery = Celery(
    __name__,
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0",
)

# celery.conf.timezone = TIMEZONE


@app.get("/")
def root():
    return {"message": "Hello World"}


@celery.task
def divide(x, y):
    import time

    # print(f"{x} / {y} = ...")

    time.sleep(12)

    return x / y

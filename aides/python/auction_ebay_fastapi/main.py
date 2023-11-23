from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def get():
    return get_about()


@app.get("/about")
def get_about():
    return "The aide for work with the eBay's auction."


@app.get("/tags")
# Tags for detect this aide.
# There is no need to repeat the tags below for your own functions.
def get_tags():
    return ["auction", "eBay"]


@app.get("/products/today/about")
# Description of this function.
def get_products_today_about():
    return "Returns a list of auction products no later than the last 24 hours."


@app.get("/products/today/tags")
# Tags for fast detect a needed function.
def get_products_today_tags():
    return ["hours", "items", "now", "products", "today"]


@app.get("/products/today")
# See [get_products_today_about], [get_products_today_tags].
def get_products_today():
    # TODO
    return {
        "result": [
            {"name": "A", "price": 1.23},
            {"name": "B", "price": 4.56},
        ],
        "parameters": {
            "hours": 24,
            "location": "Canada",
        },
    }


@app.get("/products/today/configure")
# The parameters for this function.
# See examples on https://openai.com/blog/function-calling-and-other-api-updates
def get_products_today_configure():
    return {
        "type": "object",
        "properties": {
            "hours": {
                "type": "integer",
                "about": "For how many recent hours we want to see product data.",
                "default": 24
            },
            "location": {
                "type": "string",
                "about": "The country or city and state, e.g. Canand or San Francisco, CA."
            },
        },
        "required": ["location"]
    }

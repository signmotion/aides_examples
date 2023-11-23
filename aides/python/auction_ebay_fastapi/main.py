from fastapi import FastAPI

# * Conventions
# ---------------
#   * Always skip the verb for get-functions.
#   * Order for declared endpoins:
#     * root:
#       * /about
#       * /tags
#       * /
#     * endpoints:
#       * /end/point/about
#       * /end/point/tags
#       * /end/point
#       * /end/point/configure

# For complex aide the best practic it's best to use recommendations
# by link https://fastapi.tiangolo.com/tutorial/bigger-applications
app = FastAPI(title="Auction eBay Aide")


@app.get("/about")
def root_about():
    return "The aide for work with the eBay's auction."


@app.get("/tags")
# Tags for detect this aide.
# There is no need to repeat the tags below for your own functions.
def tags():
    return ["auction", "eBay"]


@app.get("/")
def root():
    return root_about()


@app.get("/products/today/about")
# Description of this function.
def products_today_about():
    return "Returns a list of auction products no later than the last 24 hours."


@app.get("/products/today/tags")
# Tags for fast detect a needed function.
def products_today_tags():
    return ["hours", "items", "now", "products", "today"]


@app.get("/products/today")
# See [get_products_today_about], [get_products_today_tags].
def products_today():
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
def products_today_configure():
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
                "about": "The country or city and state, e.g. Canada or San Francisco, CA."
            },
        },
        "required": ["location"]
    }

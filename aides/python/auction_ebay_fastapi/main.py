from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
from dotenv import load_dotenv
import os
import httpx
import traceback


# For complex aide the best practic it's best to use recommendations
# by link https://fastapi.tiangolo.com/tutorial/bigger-applications

# ! See conventions in README.md.


is_production = False
use_test_context = True
include_original_response = False

load_dotenv(dotenv_path=Path(".env" if is_production else ".sandbox.env"))
EBAY_OAUTH_APP_TOKEN = os.getenv('EBAY_OAUTH_APP_TOKEN')

api_domain = "api.ebay.com" if is_production else "api.sandbox.ebay.com"


app = FastAPI(title="Auction eBay Aide")


# the aide character section


@app.get("/about")
def root_about():
    return "The aide for work with the eBay's auction."


@app.get("/tags")
# Tags for detect this aide.
# There is no need to repeat the tags below for your own functions.
def tags():
    return ["auction", "eBay"]


@app.get("/characteristic/age")
def characteristic_age():
    return 19


@app.get("/characteristic/face")
def characteristic_face():
    return FileResponse(Path("face.webp"))


@app.get("/characteristic/constitution")
def characteristic_constitution():
    return {
        "Posture": "Upright and alert, demonstrating attentiveness.",
        "Build": "Average, portraying approachability and practicality.",
    }


@app.get("/characteristic/clothing")
def characteristic_clothing():
    return {
        "Business casual attire": "A blend of professionalism and comfort.",
        "Essential accessories": "A wristwatch for timekeeping and possibly glasses for detailed examination of items.",
    }


@app.get("/characteristic/traits")
def characteristic_traits():
    return {
        "Analytical": "Able to assess value and condition efficiently.",
        "Decisive": "Confident in making quick purchase decisions.",
        "Detail-Oriented": "Attentive to the specifics and potential flaws of items.",
        "Patient": "Willing to wait for the right item and the right price.",
        "Knowledgeable": "Well-versed in market trends and product values.",
    }


@app.get("/")
def root():
    return root_about()


# the abilities section


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
# See [context].
def products_today():
    url = f"https://{api_domain}/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {EBAY_OAUTH_APP_TOKEN}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_ENCA",
        "X-EBAY-C-ENDUSERCTX": "affiliateCampaignId=<ePNCampaignId>,affiliateReferenceId=<referenceId>",
    }

    params = {
        "q": "iPhone",
        "sort": "newlyListed",
        "limit": "2",
    }
    # some params work in the request to the real domain
    if is_production:
        params = {
            **params,
            **{
                "filter": "buyingOptions:{AUCTION}",
            }
        }

    with httpx.Client(headers=headers) as client:
        response = client.get(url, params=params)

    if response.status_code == 200:
        r = response.json()
    else:
        ex = "Failed to retrieve data."
        print(f"!) {ex}")
        return ex

    try:
        o = {
            "total": r["total"],
            "href": r["href"],
            "next": r["next"],
            "offset": r["offset"],
            "limit": r["limit"],
            "products": [{
                "title": item["title"] if "title" in item else None,
                "condition": item["condition"] if "condition" in item else None,
                "price": item["price"] if "price" in item else None,
                "currentBidPrice": item["currentBidPrice"] if "currentBidPrice" in item else None,
            } for item in r["itemSummaries"]],

        }
    except Exception as e:
        o = {
            "error":
            {
                "key": f"{e}",
                "traceback": f"{traceback.format_exc()}",
            },
        }

    if include_original_response:
        o["original"] = r

    return o


@app.get("/products/today/demo")
def products_today_demo():
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


# the context section


ctx = {}


test_context = {
    "hours": 24,
    "location": "Canada",
    "query": "smartphone",
}


if use_test_context:
    ctx = test_context
    print("Initialized the test context.")


@app.get("/context")
# The full context of this aide.
# Use as parameters for call the functions.
# By examples in https://openai.com/blog/function-calling-and-other-api-updates
# See also [].
def context():
    print("ctx", ctx)
    return ctx


@app.get("/schema")
# The schema for the context.
def schema():
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
                "about": "The country or city and state. E.g. Canada or San Francisco, CA."
            },
            "query": {
                "type": "string",
                "about": "Auction search query. E.g. smartphone."
            },
        },
        "required": ["location", "query"]
    }


@app.get("/context/{hid}")
# The getter by Human ID (HID) from the context.
def value(hid: str):
    return ctx[hid] if hid in ctx else None


# the context's setters section
# See [context_schema].


@app.post("/hours/{v}")
def hours(v: int): ctx["hours"] = v


@app.post("/location/{v}")
def location(v: str): ctx["location"] = v


@app.post("/query/{v}")
def location(v: str): ctx["query"] = v

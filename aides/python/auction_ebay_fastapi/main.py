from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
from dotenv import load_dotenv
import os
import httpx


# * Conventions
# ---------------
#   * Structure:
#     * root endpoin
#     * endpoints
#     * context
#   * Always skip the verb for get-functions.
#   * Order for declared the endpoint `root`:
#     * /about
#     * /tags
#     * /face
#     * /
#   * Order for declared endpoints:
#     * /end/point/about
#     * /end/point/tags
#     * /end/point
#  * The context comes last.


load_dotenv()
EBAY_OAUTH_APP_TOKEN = os.getenv('EBAY_OAUTH_APP_TOKEN')

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
    domain = "api.sandbox.ebay.com"
    url = f"https://{domain}/buy/browse/v1/item_summary/search"
    headers = {
        "Authorization": f"Bearer {EBAY_OAUTH_APP_TOKEN}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_ENCA",
        "X-EBAY-C-ENDUSERCTX": "affiliateCampaignId=<ePNCampaignId>,affiliateReferenceId=<referenceId>",
    }
    print(headers)
    params = {
        "q": "iphone",
        "sort": "newlyListed",
        # "fieldgroups": "ASPECT_REFINEMENTS",
        "limit": "3",
    }
    with httpx.Client(headers=headers) as client:
        response = client.get(url, params=params)

    print(response.url)

    return response.json()


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


@app.get("/context")
# The context of this aide.
# Use as parameters for call the functions.
# By examples in https://openai.com/blog/function-calling-and-other-api-updates
def context():
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

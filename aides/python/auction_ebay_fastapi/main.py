from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
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
        "Authorization": "Bearer v^1.1#i^1#I^3#p^1#r^0#f^0#t^H4sIAAAAAAAAAOVYX2wURRjv9R9UoDyogPwp5wIx2O7e7t3e7d3KnVxbai8UWnqlrU0smdudbcfb2z12Zu0diVhpaEiMog9CjGJqFCJKAg9GgYQQEoxRX0w0YEAfjELQKCIvEIHg3F4p10qg0Ets4r1cdub7vvl+v/n+zAw/WFn15HDz8JU5rhmlI4P8YKnLJcziqyoraqvLShdWlPAFAq6RweWD5dvKLqzCIKWn5XaI06aBoTuT0g0sO4NhxrYM2QQYYdkAKYhlosjx6LoW2cvxctoyiamYOuOONYaZoMYLPh6KXj4k+oJ+kY4at2x2mGEm4Q2pkuQXFdEPBTUk0HmMbRgzMAEGCTNe3utjBYH1ih2CKPtFWZS4gM/fw7g7oYWRaVARjmcijruyo2sV+Hp3VwHG0CLUCBOJRZvirdFY45r1Has8BbYiozzECSA2Hv/VYKrQ3Ql0G959GexIy3FbUSDGjCeSX2G8UTl6y5kHcN+hGopqSOL9ClQhVCnvRaGyybRSgNzdj9wIUlnNEZWhQRDJ3otRykbieaiQ0a/11ESs0Z3722ADHWkIWmFmTX302WhbGxOJGqqFUDzLRtNpCyAM2Xh9N6toYjAU9APIaoGgSmH7RhfKWxulecJKDaahohxp2L3eJPWQeg0nciMWcEOFWo1WK6qRnEeFcoExDvme3Kbmd9Em/UZuX2GKEuF2Pu+9A2PahFgoYRM4ZmHihENRmAHpNFKZiZNOLI6GTwaHmX5C0rLHMzAwwA34ONPq83h5XvB0r2uJK/0wBRgqm8v1vDy6twKLHCgKpJoYySSbpr5kaKxSB4w+JiIKXkHiR3kf71Zk4ui/Bgowe8ZnRNEyRJF8Cq+AUDDoExQAipEhkdEg9eT8gAmQZVPASkKS1oECWYXGmZ2CFlJln1/z+oIaZNVASGPFkKaxCb8aYAUNQh7CREIJBf9PiTLZUI9DxYKkKLFetDjvatzCaxKWWtb2C20NtclQnE91D6z1dIV6UKZTTbYbzwQSyZaARXB4stlwR/ANOqLMdND1i0FALteLR0KziQlUpwQvrphp2GbqSMlOrw32WWobsEi23s7S7zjUdfo3Jag0IWPFqdhFA3mfxeLBcBevU/1HXeqOqHAucKcXqpw+pgZAGnG0D+VyPcspZspjAnoIyQ1vcrx2TxC8o5AnYWe5PhtiQj1R6Tlw0kqIFnOOtjR18ir5hklBTF6FXjJUWyEPtJDTmTnKJurrJ/i+1sxMhZSErScnr6JCoE8pRBG9akyrAKVI85CRmr8jcA5uDr+gcBbEpm3R6xHXmjsyd5hJaNADCLFMXYdWpzDl0ptK2QQkdDjdanARahGiue66Os1OSBQUH/RJgaA0JWyKc/7ZNN06SLE7533chDzj32UiJc5P2OY6xm9zHSl1uXiJZ4VafmVl2cbystkMprWHw8BQE2aGQ0DjaNkzALEtyCVhNg2QVVrpQme+U64WvAiNPMcvGHsTqioTZhU8EPGLb89UCHPnz/H6BMErCqJfFKUeftnt2XJhXvkj8luRzfuFG30iv7u2bl/8j5WR14b4OWNCLldFCQ3fkuoNSzZKX7z3zS9LT8x9+tpet3Dpx32n5u4sOXr0xBPHNz8VRoE3bjQNDp6qr/1VeS1QV/Po0svfvv741Q+W7c4cXuzaMgPtWfbmyLWzQ2cXHP94xlD/peXk50UNH6aCfe0zd/bW7PhkwfenuIuZnbsuLdpVK13uXfru9cMvr17ROkuKRX+qbGou3zPzXOuKmoUlN/UdB24mw+9UbwWHXu08edpvHjr49WPxh+BHoH4kfq5t3pUjwycPNc/r9Xx1/bxwbOWF2Z/+1t33SnfN0d+/rLi4vXJ++w+77Sr8V2PXTTH6+UvV/r+V4e2xzPW69v1nDv7ZemCr8f4R7UWmenHdw3u7hlZ/1ug7v/bt3iWn89v4D2AlKA2rEwAA",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_ENCA",
        "X-EBAY-C-ENDUSERCTX": "affiliateCampaignId=<ePNCampaignId>,affiliateReferenceId=<referenceId>",
    }
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

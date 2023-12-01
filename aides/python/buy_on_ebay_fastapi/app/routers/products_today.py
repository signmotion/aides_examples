from fastapi import APIRouter
import httpx
import traceback

from ..internal.config import *
from .context import context


router = APIRouter()


@router.get("/products-today")
# See [products_today_about], [products_today_tags].
# See [context].
def products_today(
    summary="Returns a list of recent products from auction.",
    description="Returns a list of auction products no later than the last 24 hours.",
    tags=["hours", "items", "now", "products", "today"],
):
    if use_fake_response:
        return products_today_demo_json()

    url = f"https://{api_domain}/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {ebay_oauth_app_token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_ENCA",
        "X-EBAY-C-ENDUSERCTX": "affiliateCampaignId=<ePNCampaignId>,affiliateReferenceId=<referenceId>",
    }

    params = {
        "q": context().query,
        "sort": "newlyListed",
        "limit": "2",
    }
    # some params work in the request to the real domain
    if is_production:
        params = {
            **params,
            **{
                "filter": "buyingOptions:{AUCTION}",
            },
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
            "products": [
                {
                    "title": item["title"] if "title" in item else None,
                    "condition": item["condition"] if "condition" in item else None,
                    "price": item["price"] if "price" in item else None,
                    "currentBidPrice": item["currentBidPrice"]
                    if "currentBidPrice" in item
                    else None,
                }
                for item in r["itemSummaries"]
            ],
        }
    except Exception as e:
        o = {
            "error": {
                "key": f"{e}",
                "traceback": f"{traceback.format_exc()}",
            },
        }

    if include_original_response_in_response:
        o["original_response"] = r

    return {
        "result": o,
        "context": context(),
    }


@router.get("/products-today-demo-json")
def products_today_demo_json():
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

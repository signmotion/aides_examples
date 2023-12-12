import logging
import json
from typing import Callable
import httpx
import traceback

from ..config import *
from ..packages.aide_server.src.aide_server.memo import Memo
from ..packages.aide_server.src.aide_server.task import Task


logger = logging.getLogger("uvicorn.error")


def products_today(
    task: Task,
    memo: Memo,
    publish_progress: Callable,
    publish_result: Callable,
):
    logger.info(f"Running `{__name__}`...")

    publish_progress(task=task, progress=0)

    if use_fake_response:
        result = _products_today_demo_ebay_json()
        publish_progress(task=task, progress=100)

        return publish_result(task=task, result=result)

    url = f"https://{api_domain}/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {ebay_oauth_app_token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_ENCA",
        "X-EBAY-C-ENDUSERCTX": "affiliateCampaignId=<ePNCampaignId>,affiliateReferenceId=<referenceId>",
    }

    params = {
        "q": app().memo.context.query,  # type: ignore
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
        logger.error(f"!) {ex}")
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

    result = {
        "result": o,
        "context": app().memo.context,  # type: ignore
    }
    publish_progress(task=task, progress=100)

    return publish_result(task=task, result=result)


def _products_today_demo_ebay_json():
    with open("kins/appearance/data/examples/responses/1.json", "r") as file:
        data = file.read()

    return json.loads(data)

import json
from typing import Callable
import httpx
import traceback

from ..config import *
from ..packages.aide_server.src.aide_server.log import logger
from ..packages.aide_server.src.aide_server.memo import Memo
from ..packages.aide_server.src.aide_server.task import Result, Task


async def products_today(
    task: Task,
    memo: Memo,
    publish_progress: Callable,
    publish_result: Callable,
):
    logger.info(f"Running `{__name__}`...")

    await publish_progress(task=task, progress=0)

    if use_fake_response:
        value = _products_today_demo_ebay_json()
        await publish_progress(task=task, progress=100)

        return await publish_result(
            task=task,
            result=Result(uid_task=task.uid, value=value),
        )

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

    r = response.json()
    try:
        if response.status_code != 200:
            raise Exception("Failed to retrieve data.")
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
        logger.error(o)

    if include_original_response_in_response:
        o["original_response"] = r

    value = {
        "result": o,
        "context": app().memo.context,  # type: ignore[override]
    }
    await publish_progress(task=task, progress=100)

    return await publish_result(
        task=task,
        result=Result(uid_task=task.uid, value=value),
    )


def _products_today_demo_ebay_json():
    with open("kins/appearance/data/examples/responses/1.json", "r") as file:
        data = file.read()

    return json.loads(data)

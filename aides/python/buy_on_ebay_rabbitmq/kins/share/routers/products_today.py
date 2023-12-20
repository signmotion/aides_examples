import json
import httpx
import traceback
from typing import Any, Callable, Dict, Optional

from ..config import *
from ..packages.aide_server.src.aide_server.helpers import construct_answer
from ..packages.aide_server.src.aide_server.log import logger
from ..packages.aide_server.src.aide_server.task import Result, Task


async def products_today(
    task: Task,
    publish_progress: Callable,
    publish_result: Callable,
):
    logger.info(f"Running `{__name__}`...")

    await publish_progress(task=task, progress=0)

    response_result: Optional[Dict[str, Any]] = None
    improved_result: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    while True:
        try:
            r = _query(task.context)
            response_result = {
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

            break

        except Exception as ex:
            logger.error(f"{ex} :: {traceback.format_exc()}")
            error = ex

            break

    value = construct_answer(
        improved_result=improved_result,
        raw_result=response_result if include_raw_response_in_answer else None,
        context=task.context if include_raw_response_in_answer else None,
        error=error,
    )

    await publish_progress(task=task, progress=100)

    return await publish_result(
        task=task,
        result=Result(uid_task=task.uid, value=value),
    )


def _query(context: Dict[str, Any]) -> Dict[str, Any]:
    if fake_response:
        return _products_today_demo_ebay_json()

    url = f"https://{api_domain}/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {ebay_oauth_app_token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_ENCA",
        "X-EBAY-C-ENDUSERCTX": "affiliateCampaignId=<ePNCampaignId>,affiliateReferenceId=<referenceId>",
    }

    params = {
        "q": context.query,  # type: ignore
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

    if response.status_code != 200:
        raise Exception("Failed to retrieve data.")

    logger.info(response)

    return response.json()


def _products_today_demo_ebay_json() -> Dict[str, Any]:
    with open("kins/share/data/examples/responses/1.json", "r") as file:
        data = file.read()

    return json.loads(data)

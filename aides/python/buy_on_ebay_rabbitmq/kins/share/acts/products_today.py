import json
import httpx
from pydantic import NonNegativeFloat
from typing import Any, Dict

from ..config import (
    api_domain,
    ebay_oauth_app_token,
    fake_response,
    include_context_in_answer,
    include_raw_response_in_answer,
    is_production,
)
from ..context import Context
from ..packages.aide_server.src.aide_server.helpers import (
    construct_and_publish,
    PublishProgressFn,
    PublishResultFn,
)
from ..packages.aide_server.src.aide_server.log import logger
from ..packages.aide_server.src.aide_server.task_progress_result import Task


async def products_today(
    task: Task,
    publish_progress: PublishProgressFn,
    publish_result: PublishResultFn,
):
    return await construct_and_publish(
        __name__,
        task=task,
        construct_raw_result=_construct_raw_result,
        publish_progress=publish_progress,
        publish_result=publish_result,
        fake_raw_result=_products_today_ebay_demo_json() if fake_response else None,
        include_raw_response_in_answer=include_raw_response_in_answer,
        include_context_in_answer=include_context_in_answer,
    )


async def _construct_raw_result(
    task: Task,
    publish_progress: PublishProgressFn,
    publish_result: PublishResultFn,
    start_progress: NonNegativeFloat,
    stop_progress: NonNegativeFloat,
):
    context = Context.model_validate(task.context)

    url = f"https://{api_domain}/buy/browse/v1/item_summary/search"
    headers = {
        "Authorization": f"Bearer {ebay_oauth_app_token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_ENCA",
        "X-EBAY-C-ENDUSERCTX": "affiliateCampaignId=<ePNCampaignId>,affiliateReferenceId=<referenceId>",
    }
    params: Dict[str, Any] = {
        "q": context.query,
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

    r = response.json()

    return {
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


def _products_today_ebay_demo_json() -> Dict[str, Any]:
    with open("kins/share/data/examples/responses/1.json", "r") as file:
        data = file.read()

    return json.loads(data)

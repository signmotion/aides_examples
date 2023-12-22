import datetime
from pydantic import BaseModel, Field
from typing import List

from packages.aide_server.src.aide_server.configure import Configure


class RegisteredAide(BaseModel):
    configure: Configure = Field(
        ...,
        title="Registered Aides",
        description="Available aides for Client.",
    )

    registered_date: str = Field(
        default=datetime.datetime.now().isoformat(),
        title="Registered Date",
        description="Registered date as ISO8601 format.",
    )

    updated_dates: List[str] = Field(
        default=[],
        title="Updated Dates",
        description="Updated dates as ISO8601 format. Ordered by desc.",
    )


class Context(BaseModel):
    registered_aides: List[RegisteredAide] = Field(
        default=[],
        title="Registered Aides",
        description="Available aides for Client.",
    )


def test_context_registered_aides_init():
    return Context.model_validate(
        {
            "registered_aides": [
                # Auction eBay
                {
                    "registered_date": "",
                    "updated_dates": [],
                    "configure": {
                        "name": {"en": "Auction eBay"},
                        "hid": "auction_ebay",
                        "summary": {"en": "The aide for work with the eBay's auction."},
                        "description": {
                            "en": "Appraise purchases items from eBay's auction."
                        },
                        "tags": [
                            {"en": "auction"},
                            {"en": "buy"},
                            {"en": "eBay"},
                            {"en": "purchase"},
                        ],
                        "_path_to_face": "Localy you can see a face of aide by path `http://127.0.0.1:*/face`.",
                        "path_to_face": "kins/share/data/face.webp",
                        "characteristic": {
                            "age": 19,
                            "constitution": [
                                {
                                    "en": "Posture. Upright and alert, demonstrating attentiveness."
                                },
                                {
                                    "en": "Build. Average, portraying approachability and practicality."
                                },
                            ],
                            "clothing": [
                                {
                                    "en": "Business casual attire. A blend of professionalism and comfort."
                                },
                                {
                                    "en": "Essential accessories. A wristwatch for timekeeping and possibly glasses for detailed examination of items."
                                },
                            ],
                            "traits": [
                                {
                                    "en": "Analytical. Able to assess value and condition efficiently."
                                },
                                {
                                    "en": "Decisive. Confident in making quick purchase decisions."
                                },
                                {
                                    "en": "Detail-Oriented. Attentive to the specifics and potential flaws of items."
                                },
                                {
                                    "en": "Patient. Willing to wait for the right item and the right price."
                                },
                                {
                                    "en": "Knowledgeable. Well-versed in market trends and product values."
                                },
                            ],
                        },
                        "savant_connector": "amqp://guest:guest@localhost:5672/",
                        "acts": [
                            {
                                "name": {"en": "Products Today"},
                                "hid": "products_today",
                                "summary": {
                                    "en": "Returns a list of recent products from auction."
                                },
                                "description": {
                                    "en": "Returns a list of auction products no later than the last 24 hours."
                                },
                                "tags": [
                                    {"en": "hours"},
                                    {"en": "items"},
                                    {"en": "now"},
                                    {"en": "products"},
                                    {"en": "today"},
                                ],
                                "context": {"optional": ["Hours", "Location", "Query"]},
                                "version": "0.1.0",
                            }
                        ],
                        "version": "0.1.2",
                    },
                },
                # Study Language
                {
                    "registered_date": "",
                    "updated_dates": [],
                    "configure": {
                        "name": {"en": "Study Language"},
                        "hid": "study_language",
                        "summary": {"en": "The aide for studying language."},
                        "description": {
                            "en": "The aide for learning languages. For example, English."
                        },
                        "tags": [
                            {"en": "english"},
                            {"en": "language"},
                            {"en": "learn"},
                            {"en": "study"},
                            {"en": "teach"},
                            {"en": "ukrainian"},
                        ],
                        "_path_to_face": "Localy you can see a face of aide by path `http://127.0.0.1:*/face`.",
                        "path_to_face": "kins/share/data/face.webp",
                        "characteristic": {
                            "age": 30,
                            "constitution": [
                                {
                                    "en": "A composed and confident demeanor, possibly a medium build, reflecting a balance of approachability and authority."
                                }
                            ],
                            "clothing": [
                                {
                                    "en": "Professional yet approachable attire, such as smart casual. Clothes should be neat and tidy, giving an impression of professionalism without being overly formal."
                                }
                            ],
                            "traits": [
                                {
                                    "en": "Patience, articulate, encouraging, attentive, knowledgeable about language nuances, and culturally sensitive."
                                }
                            ],
                        },
                        "savant_connector": "amqp://guest:guest@localhost:5672/",
                        "acts": [
                            {
                                "name": {"en": "Phrasal Verbs"},
                                "hid": "phrasal_verbs",
                                "summary": {
                                    "en": "Extracts phrasal verbs from [text] and translates these verbs."
                                },
                                "description": {
                                    "en": "Returns extracted phrasal verbs from [text]. Also translates these verbs."
                                },
                                "tags": [
                                    {"en": "extract"},
                                    {"en": "phrasal verbs"},
                                    {"en": "translate"},
                                ],
                                "context": {"required": ["Text Source"]},
                                "version": "0.1.0",
                            },
                            {
                                "name": {"en": "Translate Caption."},
                                "hid": "translate_caption",
                                "summary": {
                                    "en": "Translates the caption and subtitle to other language."
                                },
                                "description": {
                                    "en": "Return the translated caption and subtitle to other language."
                                },
                                "tags": [
                                    {"en": "caption"},
                                    {"en": "subtitle"},
                                    {"en": "translate"},
                                ],
                                "context": {
                                    "required": ["Text Source", "Target Language"]
                                },
                                "version": "0.1.0",
                            },
                        ],
                        "version": "0.2.0",
                    },
                },
            ],
        }
    )

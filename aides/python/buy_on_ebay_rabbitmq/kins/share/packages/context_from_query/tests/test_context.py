import unittest

from ..src.context_from_query.context import Context
from ..src.context_from_query.extractors import extract_data_spacy
from ..src.context_from_query.meaning_data import MeaningData
from ..src.context_from_query.translators import translate_time_in_minutes


class TestContext(unittest.TestCase):
    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName=methodName)
        self.maxDiff = None

    def test_context_with_one_country(self):
        query = "Tell me about Ukraine."
        expected = Context.model_validate(
            {
                "slice": {
                    "raw": {
                        MeaningData.GPE: [
                            {"i": 0, "v": "Ukraine"},
                        ],
                    }
                },
                "queries": [
                    query,
                ],
            }
        )

        context = Context()
        context += query
        self.assertEqual(expected.queries, context.queries)
        self.assertEqual(expected.slice, context.slice)

    def test_context_with_two_country(self):
        query = "Tell me about Ukraine and Germany."
        expected = Context.model_validate(
            {
                "slice": {
                    "raw": {
                        MeaningData.GPE: [
                            {"i": 0, "v": "Ukraine"},
                            {"i": 0, "v": "Germany"},
                        ],
                    }
                },
                "queries": [
                    query,
                ],
            }
        )

        context = Context()
        context += query
        self.assertEqual(expected.queries, context.queries)
        self.assertEqual(expected.slice, context.slice)

    def test_context_with_give_me_products_from_ebay_canada(self):
        query = "Give me eBay auction items from the last 2 hours in Canada."
        expected = Context.model_validate(
            {
                "slice": {
                    "raw": {
                        MeaningData.GPE: [
                            {"i": 0, "v": "Canada"},
                        ],
                        MeaningData.ORG: [
                            {"i": 0, "v": "eBay"},
                        ],
                        MeaningData.TIME: [
                            {"i": 0, "v": "the last 2 hours"},
                        ],
                    },
                },
                "queries": [
                    query,
                ],
            }
        )

        context = Context()
        context += query
        self.assertEqual(expected.queries, context.queries)
        self.assertEqual(expected.slice, context.slice)

    def test_context_with_give_me_products_from_ebay_canada_h(self):
        query = "Give me eBay auction items from the last 2 hours in Canada."

        context = Context(translates=[translate_time_in_minutes])
        context += query
        self.assertEqual(2 * 60, context.slice[MeaningData.TIME.value][0].v)

    def test_context_with_give_me_products_from_ebay_canada_hm(self):
        query = "Give me eBay auction items from the last 2 hours 30 min in Canada."

        context = Context(translates=[translate_time_in_minutes])
        context += query
        self.assertEqual(2 * 60 + 30, context.slice[MeaningData.TIME.value][0].v)

    # TODO Detect a product category.
    # def test_context_with_give_me_iphones_from_ebay_canada_hm(self):
    #     query = (
    #         "Give me iPhone 12 PRO from eBay auction from the last 12 hours in Canada."
    #     )
    #     expected = ...

    #     context = Context(
    #         extract=extract_data_spacy,
    #         translates=[translate_time_in_minutes],
    #     )
    #     context += query
    #     self.assertEqual(expected.slice, context.slice)


if __name__ == "main":
    unittest.main()

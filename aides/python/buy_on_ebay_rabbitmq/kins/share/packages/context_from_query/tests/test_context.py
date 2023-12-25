import unittest

from ..src.context_from_query.context import Context
from ..src.context_from_query.meaning_data import MeaningData


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

        context: Context = Context()
        context.add(query)
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

        context: Context = Context()
        context.add(query)
        self.assertEqual(expected.queries, context.queries)
        self.assertEqual(expected.slice, context.slice)

    def test_context_with_give_me_products_from_ebay(self):
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

        context: Context = Context()
        context.add(query)
        self.assertEqual(expected.queries, context.queries)
        self.assertEqual(expected.slice, context.slice)


if __name__ == "main":
    unittest.main()

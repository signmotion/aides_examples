import unittest

from ..src.context_from_query.context import Context
from ..src.context_from_query.meaning_data import MeaningData


class TestContext(unittest.TestCase):
    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName=methodName)
        self.maxDiff = None

    query_1 = "Tell me about Ukraine."

    def test_context_with_one_country(self):
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
                    self.query_1,
                ],
            }
        )

        context: Context = Context()
        context.add(self.query_1)
        print(expected)
        print(context)
        self.assertEqual(expected.queries, context.queries)
        self.assertEqual(expected.slice, context.slice)


if __name__ == "main":
    unittest.main()

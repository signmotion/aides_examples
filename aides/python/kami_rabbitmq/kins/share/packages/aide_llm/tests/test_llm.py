from typing import List
import unittest

from ..src.aide_llm.aide_llm import AideLlm


class TestLlm(unittest.TestCase):
    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName=methodName)
        self.maxDiff = None

    def test_question_about_capital(self):
        # model_name = "mistral-7b-instruct-v0.2.Q6_K.gguf"
        model_name = "mistral-7b-openorca.Q4_0.gguf"
        model_path = "aide_llm/tests/data/models/llms/"
        llm = AideLlm(model_name, model_path=model_path, verbose=True)

        tokens: List[str] = []
        prompt = "The capital of France is"
        max_tokens = 12
        for token in llm.generate(prompt, max_tokens=max_tokens):
            tokens.append(token)
        self.assertGreater(len(tokens), max_tokens / 2)
        self.assertLessEqual(len(tokens), max_tokens)

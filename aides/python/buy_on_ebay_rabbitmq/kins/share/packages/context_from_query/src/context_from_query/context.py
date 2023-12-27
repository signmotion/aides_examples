from flair.data import Sentence
from flair.nn import Classifier
import logging
from pydantic import BaseModel, Field
from typing import Any, List

from .detectors import default_detect_meaning_data, DetectMeaningDataFn
from .extractors import default_extract_data, ExtractFn
from .translators import default_base_translate, TranslateFn
from .slice import Slice

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Context(BaseModel):
    """
    Recognize data from queries and fill it to `Slice`.
    """

    # TODO Grant add queries into constructor. See https://github.com/pydantic/pydantic/issues/1729
    # def model_post_init(self):
    # qs = self.queries.copy()
    # self.queries.clear()
    # for q in qs:
    #     self.add(q)

    def __iadd__(self, query: Any):
        """
        Add a non empty `query` to context and recognize the added query.

        Usage:
            context += "I love Ukraine."
        """

        assert isinstance(query, str), "Not implemented. TODO"

        self.add(query)

        return self

    def add(self, query: Any):
        """
        Add a non empty `query` to context and recognize the added query.

        Usage:
            context.add("I love Ukraine.")
        """

        assert isinstance(query, str), "Not implemented. TODO"

        q = query.strip()
        if q:
            i = len(self.queries)
            self.queries.append(q)
            self.fill_slice(i, q)

    slice: Slice = Field(
        default=Slice(),
        title="Slice",
        description="A slice of data extracted from queries.",
    )

    queries: List[Any] = Field(
        default=[],
        title="Queries",
        description="Queries for data extraction to `Slice`.",
    )

    extract: ExtractFn = Field(
        default=default_extract_data,
        title="Extract",
        description="Extract data from `query`.",
    )

    detect: DetectMeaningDataFn = Field(
        default=default_detect_meaning_data,
        title="Meaning Data Detector",
        description="Detect `MeaningData` by string value.",
    )

    base_translate: TranslateFn = Field(
        default=default_base_translate,
        title="Base Translator",
        description="Base translate `LabeledQuery` to `Slice`. Call before `translates`.",
    )

    translates: List[TranslateFn] = Field(
        default=[],
        title="Translators",
        description="Translate `LabeledQuery` to `Slice`. Call sequentially after `base_translate`.",
    )

    def fill_slice(self, index_query: int, query: Any):
        """
        Fill the `slice` with query.

        See https://flairnlp.github.io/docs/tutorial-basics/tagging-entities for details.
        See demo section in the code below.
        """

        # demo
        # uncomment for show results of available models
        # sentence = Sentence(self.queries[-1])
        # self._tagging_entities_demo(sentence)
        # self._tagging_sentiment_demo(sentence)
        # self._tagging_and_linking_entities_demo(sentence)
        # self._tagging_part_of_speech_demo(sentence)
        # self._tagging_other_things_demo(sentence)

        # analyze & fill
        labeled_query = self.extract(query)
        self.base_translate(index_query, labeled_query, self.slice)

        for translate in self.translates:
            translate(index_query, labeled_query, self.slice)

        self.slice.sort()

    def _tagging_entities_demo(self, sentence: Sentence):
        # Dictionary with 20 tags: <unk>, O, S-ORG, S-MISC, B-PER, E-PER, S-LOC, B-ORG,
        # E-ORG, I-PER, S-PER, B-MISC, I-MISC, E-MISC, I-ORG, B-LOC, E-LOC, I-LOC, <START>, <STOP>
        self._fill_demo(sentence, "ner")
        self._fill_demo(sentence, "ner-fast")
        self._fill_demo(sentence, "ner-large")

        # Dictionary with 75 tags: O, S-PERSON, B-PERSON, E-PERSON, I-PERSON, S-GPE, B-GPE,
        # E-GPE, I-GPE, S-ORG, B-ORG, E-ORG, I-ORG, S-DATE, B-DATE, E-DATE, I-DATE, S-CARDINAL,
        # B-CARDINAL, E-CARDINAL, I-CARDINAL, S-NORP, B-NORP, E-NORP, I-NORP, S-MONEY, B-MONEY,
        # E-MONEY, I-MONEY, S-PERCENT, B-PERCENT, E-PERCENT, I-PERCENT, S-ORDINAL, B-ORDINAL,
        # E-ORDINAL, I-ORDINAL, S-LOC, B-LOC, E-LOC, I-LOC, S-TIME, B-TIME, E-TIME, I-TIME,
        # S-WORK_OF_ART, B-WORK_OF_ART, E-WORK_OF_ART, I-WORK_OF_ART, S-FAC
        self._fill_demo(sentence, "ner-ontonotes")
        self._fill_demo(sentence, "ner-ontonotes-fast")
        # Dictionary with 76 tags: <unk>, O, B-CARDINAL, E-CARDINAL, S-PERSON, S-CARDINAL,
        # S-PRODUCT, B-PRODUCT, I-PRODUCT, E-PRODUCT, B-WORK_OF_ART, I-WORK_OF_ART, E-WORK_OF_ART,
        # B-PERSON, E-PERSON, S-GPE, B-DATE, I-DATE, E-DATE, S-ORDINAL, S-LANGUAGE, I-PERSON,
        # S-EVENT, S-DATE, B-QUANTITY, E-QUANTITY, S-TIME, B-TIME, I-TIME, E-TIME, B-GPE, E-GPE,
        # S-ORG, I-GPE, S-NORP, B-FAC, I-FAC, E-FAC, B-NORP, E-NORP, S-PERCENT, B-ORG, E-ORG,
        # B-LANGUAGE, E-LANGUAGE, I-CARDINAL, I-ORG, S-WORK_OF_ART, I-QUANTITY, B-MONEY
        self._fill_demo(sentence, "ner-ontonotes-large")

    def _tagging_sentiment_demo(self, sentence: Sentence):
        self._fill_demo(sentence, "sentiment")
        self._fill_demo(sentence, "sentiment-fast")

    def _tagging_and_linking_entities_demo(self, sentence: Sentence):
        self._fill_demo(sentence, "linker")

    def _tagging_part_of_speech_demo(self, sentence: Sentence):
        self._fill_demo(sentence, "pos")
        self._fill_demo(sentence, "pos-fast")
        self._fill_demo(sentence, "upos")
        self._fill_demo(sentence, "upos-fast")
        # self._fill(sentence, "pos-multi")
        # self._fill(sentence, "pos-multi-fast")

    def _tagging_other_things_demo(self, sentence: Sentence):
        self._fill_demo(sentence, "chunk")
        self._fill_demo(sentence, "chunk-fast")
        self._fill_demo(sentence, "frame")
        self._fill_demo(sentence, "frame-fast")

    def _fill_demo(self, sentence: Sentence, model: str):
        logger.info(f"\nModel {model}")
        tagger = Classifier.load(model)
        tagger.predict(sentence)
        logger.info(f"\t{sentence}")

        for label in sentence.get_labels():
            logger.info(label)

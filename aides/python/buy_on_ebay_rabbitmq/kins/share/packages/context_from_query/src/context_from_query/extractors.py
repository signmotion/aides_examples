import logging
from flair.data import Sentence, Span
from flair.nn import Classifier
from typing import Any, Callable, List

from .detectors import default_detect_meaning_data, DetectMeaningDataFn
from .label import Label, LabeledQuery


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# (query)
ExtractFn = Callable[[Any], LabeledQuery]


def default_extract_data(
    query: Any,
    detect_meaning_data: DetectMeaningDataFn = default_detect_meaning_data,
) -> LabeledQuery:
    sentence = Sentence(query)

    model = "ner-ontonotes-fast"
    logger.info(f"\nModel {model}")
    tagger = Classifier.load(model)
    tagger.predict(sentence)
    logger.info(f"\t{sentence}")

    labels: List[Label] = []
    for label in sentence.get_labels():
        logger.info(label)
        assert isinstance(label.data_point, Span), "Not implemented. TODO?"

        labels.append(
            Label(
                value=detect_meaning_data(label.value),
                score=label.score,
                data=label.data_point.text,
            )
        )

    return LabeledQuery(query=query, labels=labels)

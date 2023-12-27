import logging
from flair.data import Sentence, Span
from flair.nn import Classifier
import spacy
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
    return extract_data_spacy(query, detect_meaning_data)


def extract_data_flair(
    query: Any,
    detect_meaning_data: DetectMeaningDataFn = default_detect_meaning_data,
    model: str = "ner-ontonotes-fast",
) -> LabeledQuery:
    logger.info(f"\nModel {model}")
    tagger = Classifier.load(model)

    sentence = Sentence(query)
    tagger.predict(sentence)
    logger.info(f"\t{sentence}")

    labels: List[Label] = []
    for label in sentence.get_labels():
        logger.info(f"\t{label}")
        assert isinstance(label.data_point, Span), "Not implemented. TODO?"

        labels.append(
            Label(
                value=detect_meaning_data(label.value),
                score=label.score,
                data=label.data_point.text,
            )
        )

    return LabeledQuery(query=query, labels=labels)


def extract_data_spacy(
    query: Any,
    detect_meaning_data: DetectMeaningDataFn = default_detect_meaning_data,
    model: str = "en_core_web_sm",
) -> LabeledQuery:
    logger.info(f"\nModel {model}")
    tagger = spacy.load(model)

    r = tagger(query)
    logger.info(r)

    labels: List[Label] = []
    for ent in r.ents:
        logger.info(f"\t{ent.label_} : {ent.text}")

        labels.append(
            Label(
                value=detect_meaning_data(ent.label_),
                score=1.0,
                data=ent.text,
            )
        )

    return LabeledQuery(query=query, labels=labels)

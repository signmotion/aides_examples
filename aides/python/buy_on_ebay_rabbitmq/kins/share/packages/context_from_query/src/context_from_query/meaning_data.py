from enum import Enum


class MeaningData(Enum):
    """
    Tags for classify data.

    Source: https://huggingface.co/flair/ner-english-ontonotes-large
    """

    CARDINAL = "cardinal_value"
    DATE = "date_value"
    EVENT = "event_name"
    FAC = "building_name"
    GPE = "geo_political_entity"
    LANGUAGE = "language_name"
    LAW = "law_name"
    LOC = "location_name"
    MONEY = "money_name"
    NORP = "affiliation"
    ORDINAL = "ordinal_value"
    ORG = "organization_name"
    PERCENT = "percent_value"
    PERSON = "person_name"
    PRODUCT = "product_name"
    QUANTITY = "quantity_value"
    TIME = "time_value"
    WORK_OF_ART = "work_of_art_name"

    # Is a good idea for keep text for processing, images, audio, raw bytes, etc. like "meaning data"?
    # See class `DataPoint` from Flair.
    AUDIO = "audio"
    BYTES = "bytes"
    IMAGE = "image"
    TEXT = "text"

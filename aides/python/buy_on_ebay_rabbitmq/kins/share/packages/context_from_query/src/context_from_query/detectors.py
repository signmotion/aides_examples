from typing import Callable

from .meaning_data import MeaningData

# (label_value)
DetectMeaningDataFn = Callable[[str], MeaningData]


def default_detect_meaning_data(value: str) -> MeaningData:
    # just return type by it name
    return MeaningData[value]

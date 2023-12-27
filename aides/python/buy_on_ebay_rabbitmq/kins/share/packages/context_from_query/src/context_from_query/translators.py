import re
from typing import Callable

from .label import LabeledQuery
from .meaning_data import MeaningData
from .slice import Slice, ValueSlice


# Fill `Slice` with `LabeledQuery`
# (index_query, labeled_query, slice)
TranslateFn = Callable[[int, LabeledQuery, Slice], None]


def default_base_translate_labeled_data(
    index_query: int,
    labeled_query: LabeledQuery,
    slice: Slice,
):
    for label in labeled_query.labels:
        key = label.value.value
        slice[key].append(ValueSlice(i=index_query, v=label.data))


def translate_time_in_minutes(
    index_query: int,
    labeled_query: LabeledQuery,
    slice: Slice,
):
    for vs in slice[MeaningData.TIME.value]:
        v = str(vs.v).lower()
        extracted_numbers = re.findall(r"\d+", v)
        if not bool(extracted_numbers):
            vs.v = 0
            return

        r = 0
        last_number = int(extracted_numbers[-1])
        prelast_number = int(extracted_numbers[-2]) if len(extracted_numbers) > 1 else 0

        detect_hours = any(word in v for word in ["h", "hour", "hours"])
        if detect_hours:
            r = 60 * (prelast_number if prelast_number != 0 else last_number)

        detect_minutes = any(word in v for word in ["m", "min", "minute", "minutes"])
        if detect_minutes:
            r += prelast_number if prelast_number != 0 else last_number

        vs.v = r

from enum import Enum


class TypeQueue(Enum):
    QUERY = 1
    REQUEST_PROGRESS = 2
    RESPONSE_PROGRESS = 3
    REQUEST_RESULT = 4
    RESPONSE_RESULT = 5
    PROGRESS = 6
    RESULT = 7
    LOG = 12

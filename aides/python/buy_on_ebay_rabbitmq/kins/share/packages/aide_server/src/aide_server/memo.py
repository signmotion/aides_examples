from typing import TypeVar, Generic


C = TypeVar("C")


class Memo(Generic[C]):
    def __init__(self, context: C):
        self.context = context


class NoneMemo(Memo):
    def __init__(self):
        self.context = None

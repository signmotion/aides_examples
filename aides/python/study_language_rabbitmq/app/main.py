from .internal.context import Context, test_context_smarthone
from .internal.config import use_test_context
from .routers import about, phrasal_verbs, translate_caption

from .packages.aide_server.src.aide_server.server import (
    AideServer,
    Memo,
)

# ! See conventions in ../README.md.


_app = AideServer(
    title="Study Language Aide",
    summary="The aide for studying language.",
    description="The aide for learning languages. For example, English.",
    version="0.1.1",
    tags=[
        "english",
        "language",
        "learning",
        "study",
        "teach",
        "ukrainian",
    ],
    external_routers=[
        about.router,
        phrasal_verbs.router,
        translate_caption.router,
    ],
    memo=Memo(test_context_smarthone() if use_test_context else Context()),
)


def app():
    return _app


# See `internal/context.py` and [memo] in [AideServer].
# See `routers/about.py`.
# See `routers/*.py`.

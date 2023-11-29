from fastapi import FastAPI
from .routers import about, context, phrasal_verbs, translate_caption


# ! See conventions in README.md.
# See the descriptions for the functions in the project `auction_ebay_fast_api`.


app = FastAPI(title="Study Language Aide")

app.include_router(about.router)
app.include_router(context.router)
app.include_router(phrasal_verbs.router)
app.include_router(translate_caption.router)


# the aide character section
# See `routers/about.py`.


# the abilities section
# See `routers/phrasal_verbs.py`.


# the context section
# See `routers/context.py`.

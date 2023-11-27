from fastapi import Body, FastAPI
from .routers import about, context, phrasal_verbs


# ! See conventions in README.md.
# See the descriptions for the functions in the project `auction_ebay_fast_api`.


is_production = False
use_test_context = True
fake_response = True

include_context_in_answer = True
include_original_response_in_answer = True

# The answer will be formatted to JSON.
map_answer = True

# The answer will be improved: without duplicates.
improve_answer = True

max_count_request_errors = 3


app = FastAPI(title="Study Language Aide")

app.include_router(about.router)
app.include_router(context.router)
app.include_router(phrasal_verbs.router)


# the aide character section
# See `routers/about.py`.


# the abilities section
# See `routers/phrasal_verbs.py`.


# the context section
# See `routers/context.py`.

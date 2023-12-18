from dotenv import load_dotenv
import os


is_production = False

# test_nickname_act = "phrasal_verbs"
test_nickname_act = "translate_caption"
use_test_context = bool(test_nickname_act)

fake_response = True

include_context_in_answer = False
include_raw_response_in_answer = True

# The answer will be formatted to JSON.
map_answer = True

# The answer will be improved: without duplicates.
improve_answer = True

max_count_request_errors = 1


load_dotenv()

# override defaults with values
_default_envs = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
}
for key, value in _default_envs.items():
    os.environ[key] = value  # type: ignore[override]

open_api_key = os.environ["OPENAI_API_KEY"]

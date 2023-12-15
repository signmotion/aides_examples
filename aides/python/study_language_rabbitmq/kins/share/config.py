import g4f
from dotenv import load_dotenv
import os


is_production = False
use_test_context = True
fake_response = True

use_chat_gpt = False

include_context_in_answer = False
include_raw_response_in_answer = True

# The answer will be formatted to JSON.
map_answer = True

# The answer will be improved: without duplicates.
improve_answer = True

max_count_request_errors = 1 if use_chat_gpt else 3


# gpt4free
g4f.debug.logging = True
g4f.check_version = False

load_dotenv()

# override defaults with values
_default_envs = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
}
for key, value in _default_envs.items():
    os.environ[key] = value

open_api_key = os.environ["OPENAI_API_KEY"]

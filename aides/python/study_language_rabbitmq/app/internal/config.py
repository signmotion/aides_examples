import g4f
from dotenv import load_dotenv
import os


is_production = False
use_test_context = True
fake_response = False

use_chat_gpt = True

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
print(g4f.version)
print(g4f.Provider.Ails.params)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

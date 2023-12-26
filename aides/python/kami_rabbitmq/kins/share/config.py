from dotenv import load_dotenv
import os


is_production = False
use_test_context = True
fake_response = False

include_context_in_answer = True
include_raw_response_in_answer = True

include_original_response_in_response = False

load_dotenv(dotenv_path=".env" if is_production else ".dev.env")

# override defaults with values
_default_envs = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
}
for key, value in _default_envs.items():
    os.environ[key] = value  # type: ignore[override]

open_api_key = os.environ["OPENAI_API_KEY"]

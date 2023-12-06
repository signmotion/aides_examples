from dotenv import load_dotenv
import os


is_production = False
use_test_context = True
use_fake_response = True
include_original_response_in_response = False

load_dotenv(dotenv_path=".env" if is_production else ".sandbox.env")

# override defaults with values
_default_envs = {
    "API_DOMAIN": os.getenv("API_DOMAIN"),
    "EBAY_OAUTH_APP_TOKEN": os.getenv("EBAY_OAUTH_APP_TOKEN"),
}
for key, value in _default_envs.items():
    os.environ[key] = value

api_domain = os.environ["API_DOMAIN"]
ebay_oauth_app_token = os.environ["EBAY_OAUTH_APP_TOKEN"]

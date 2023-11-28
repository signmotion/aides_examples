import g4f


is_production = False
use_test_context = False
fake_response = False

include_context_in_answer = True
include_original_response_in_answer = True

# The answer will be formatted to JSON.
map_answer = True

# The answer will be improved: without duplicates.
improve_answer = True

max_count_request_errors = 3


# gpt4free
g4f.debug.logging = True
g4f.check_version = False
print(g4f.version)
print(g4f.Provider.Ails.params)

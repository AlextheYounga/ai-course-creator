import json
from src.utils.compile_output import compile_output

print(json.dumps(compile_output(), indent=1))
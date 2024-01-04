import json
from src.utils.compile_course_material import compile_course_material

print(json.dumps(compile_course_material(), indent=1))
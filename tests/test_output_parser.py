import json
from src.mapping.map_course_material_to_server_payload import *

print(json.dumps(map_course_material_to_server_payload(), indent=1))
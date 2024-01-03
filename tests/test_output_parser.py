import json
from app.controllers.output_controller import output_controller

print(json.dumps(output_controller(), indent=1))
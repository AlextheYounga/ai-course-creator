from src.utils.files import read_json_file
import yaml

json_content = read_json_file('tests/fixtures/series.json')
yaml_content = yaml.dump(json_content)
print(yaml_content)
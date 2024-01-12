from src.openai.openai_handler import OpenAiHandler
import markdown
import yaml
from bs4 import BeautifulSoup


handler = OpenAiHandler("test")

def _get_yaml_content_from_response(path: str):
    mock_response = open(path).read()
    html = markdown.markdown(mock_response, extensions=['fenced_code'])
    soup = BeautifulSoup(html, 'html.parser')
    code_block = soup.find('code')
    return code_block.get_text()

def test_bad_yaml_with_misplaced_colons_scenario_1():
    yaml_content = _get_yaml_content_from_response('test/fixtures/responses/bad-yaml-response.md')
    repaired_content = handler.attempt_repair_yaml_content(yaml_content)
    assert len(repaired_content) == 2


def test_bad_yaml_with_misplaced_colons_scenario_2():
    yaml_content = _get_yaml_content_from_response('test/fixtures/responses/bad-yaml-response-2.md')
    repaired_content = handler.attempt_repair_yaml_content(yaml_content)
    assert len(repaired_content) == 10


def test_bad_yaml_with_misplaced_colons_scenario_3():
    yaml_content = _get_yaml_content_from_response('test/fixtures/responses/bad-yaml-response-3.md')
    repaired_content = handler.attempt_repair_yaml_content(yaml_content)
    assert len(repaired_content) == 2


def test_does_not_effect_good_yaml():
    yaml_content = _get_yaml_content_from_response('test/fixtures/responses/good-yaml-response.md')
    unaffected_content = handler.attempt_repair_yaml_content(yaml_content)
    assert unaffected_content == yaml.safe_load(yaml_content)
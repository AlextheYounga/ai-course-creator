from src.utils.files import read_yaml_file, read_json_file
from src.openai.outlines.build_master_outline import MasterOutlineBuilder
from .mocks.openai_mock_service import OpenAIMockService

OUTPUT_PATH = "test/out/course_material"
REPLACE_KEYS = ["{topic}", "{draft_outline}", "{skills}", "{page_name}"]
EXPECTED_COURSE_OUTLINE_RESPONSE = open('test/fixtures/responses/course-outline.md').read()
PARSED_DRAFT_OUTLINE = read_yaml_file('test/fixtures/data/draft-outline.yaml')
PARSED_SKILLS = read_yaml_file('test/fixtures/data/skills.yaml')

client = OpenAIMockService("Test")
builder = MasterOutlineBuilder("Ruby on Rails", client, OUTPUT_PATH)


def test_build_draft_prompt():
    course_name = PARSED_DRAFT_OUTLINE[0]['courseName']
    modules = PARSED_DRAFT_OUTLINE[0]['modules']
    prompt = builder.build_optimize_outline_prompt(course_name, PARSED_DRAFT_OUTLINE, modules)

    system_prompt = prompt[0]['content']
    user_prompt = prompt[1]['content']

    assert len(prompt) == 2

    for key in REPLACE_KEYS:
        assert key not in user_prompt
        assert key not in system_prompt


from src.utils.files import read_yaml_file
from src.openai.outlines.build_master_outline import MasterOutlineBuilder
from src.openai.openai_handler import OpenAiHandler

OUTPUT_PATH = "test/out"
EXPECTED_COURSE_OUTLINE_RESPONSE = open('test/fixtures/responses/course-outline.md').read()
PARSED_DRAFT_OUTLINE = read_yaml_file('test/fixtures/data/draft-outline.yaml')
PARSED_SKILLS = read_yaml_file('test/fixtures/data/skills.yaml')

client = OpenAiHandler("Test")
builder = MasterOutlineBuilder("Ruby on Rails", client, OUTPUT_PATH)


def test_build_draft_prompt():
    replace_keys = ["{topic}", "{draft_outline}"]
    course_name = PARSED_DRAFT_OUTLINE[0]['courseName']
    modules = PARSED_DRAFT_OUTLINE[0]['modules']
    prompt = builder.build_optimize_outline_prompt(course_name, PARSED_DRAFT_OUTLINE, modules)

    system_prompt = prompt[0]['content']
    user_prompt = prompt[1]['content']

    assert len(prompt) == 2

    for key in replace_keys:
        assert key not in user_prompt
        assert key not in system_prompt


def test_parse_optimize_course_outline_response():
    course_outline = builder.handle_course_optimize_response(EXPECTED_COURSE_OUTLINE_RESPONSE)
    data = course_outline['dict']

    assert len(data) == 5

    for item in data:
        assert item['chapter'] is not None
        assert len(item['pages']) > 0

from src.utils.files import read_yaml_file
from src.openai.outlines.draft_course_outline import OutlineDraft
from src.openai.openai_handler import OpenAiHandler

OUTPUT_PATH = "test/out"
EXPECTED_DRAFT_OUTLINE_RESPONSE = open('test/fixtures/responses/draft-outline.md').read()
PARSED_SKILLS = read_yaml_file('test/fixtures/data/skills.yaml')

client = OpenAiHandler("Test")
draft = OutlineDraft("Ruby on Rails", client, OUTPUT_PATH)


def test_build_draft_prompt():
    prompt = draft.build_draft_prompt(PARSED_SKILLS)

    assert len(prompt) == 2


def test_parse_draft_response():
    draft_outline = draft.handle_outline_draft_response(EXPECTED_DRAFT_OUTLINE_RESPONSE)
    data = draft_outline['dict']

    assert len(data) == 15

    for item in data:
        modules = item['modules']
        
        assert item['courseName'] is not None
        assert len(modules) == 2

        for module in modules:
            assert module['name'] is not None
            assert len(module['skills']) > 0

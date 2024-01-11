from src.openai.outlines.generate_skills import SkillGenerator
from .mocks.openai_mock_service import OpenAIMockService

OUTPUT_PATH = "test/out/course_material"
REPLACE_KEYS = ["{topic}", "{draft_outline}", "{skills}", "{page_name}"]
EXPECTED_SKILLS_RESPONSE = open('test/fixtures/responses/skills.md').read()

client = OpenAIMockService("Test")
generator = SkillGenerator("Ruby on Rails", client, OUTPUT_PATH)


def test_build_skills_prompt():
    prompt = generator.build_skills_prompt()

    assert len(prompt) == 2

    system_prompt = prompt[0]['content']
    user_prompt = prompt[1]['content']

    for key in REPLACE_KEYS:
        assert key not in user_prompt
        assert key not in system_prompt


def test_parse_skills_response():
    skills = generator.handle_skills_response(EXPECTED_SKILLS_RESPONSE)
    data = skills['dict']

    assert len(data) == 8

    for item in data:
        assert item['category'] is not None
        assert len(item['skills']) == 3

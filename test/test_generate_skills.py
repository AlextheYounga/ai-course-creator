from src.openai.outlines.generate_skills import SkillGenerator
from src.openai.openai_handler import OpenAiHandler

EXPECTED_SKILLS_RESPONSE = open('test/fixtures/responses/skills.md').read()

client = OpenAiHandler("Test")
generator = SkillGenerator("Ruby on Rails", client)


def test_build_skills_prompt():
    prompt = generator.build_skills_prompt()

    assert len(prompt) == 2


def test_parse_skills_response():
    skills = generator.handle_skills_response(EXPECTED_SKILLS_RESPONSE)
    data = skills['dict']

    assert len(data) == 15

    for item in data:
        assert item['category'] is not None
        assert len(item['skills']) == 3

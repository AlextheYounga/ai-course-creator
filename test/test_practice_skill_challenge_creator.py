from src.utils.files import read_json_file
from src.openai.practice_skill_challenge_creator import PracticeSkillChallengeCreator
from .mocks.openai_mock_service import OpenAIMockService

OUTPUT_PATH = "test/out"
MASTER_OUTLINE = read_json_file("test/fixtures/data/post-material-master-outline.json")

client = OpenAIMockService("Test")
creator = PracticeSkillChallengeCreator("Ruby on Rails", client, OUTPUT_PATH)

def test_build_datasets():
    for course in MASTER_OUTLINE['courses']:
        prompt = creator.prepare_datasets(course)
        assert len(prompt) == 25
        break

def test_build_prompt():
    for course in MASTER_OUTLINE['courses']:
        prompt = creator.build_skill_challenge_prompt(course)
        assert len(prompt) == 27
        break

    # Count tokens
    # The model returns 4096 tokens and we don't want to overrun the context window.
    max_tokens = 16385 - 4096 
    prompt_string = str(prompt)
    characters = len(prompt_string)
    tokens = characters / 4 # => 11650

    assert tokens < max_tokens 
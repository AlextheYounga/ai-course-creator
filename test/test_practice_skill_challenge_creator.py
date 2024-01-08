from src.openai.practice_skill_challenge_creator import PracticeSkillChallengeCreator
from .mocks.openai_mock_service import OpenAIMockService

OUTPUT_PATH = "test/out"
client = OpenAIMockService("Test")
creator = PracticeSkillChallengeCreator("Ruby on Rails", client, OUTPUT_PATH)

def test_build_datasets():
    datasets = creator.prepare_datasets('ruby-fundamentals')   
    assert len(datasets) == 25

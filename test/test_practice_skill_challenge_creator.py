from src.utils.files import read_json_file, unzip_folder
from src.openai.practice_skill_challenge_creator import PracticeSkillChallengeCreator
from .mocks.openai_mock_service import OpenAIMockService
import os
import shutil

OUTPUT_PATH = "test/out/course_material"
MASTER_OUTLINE = read_json_file("test/fixtures/data/master-outline-2.json")

def _setup_test():
    # Setup output folder
    if (os.path.exists(f"{OUTPUT_PATH}")):
        shutil.rmtree(f"{OUTPUT_PATH}")
    unzip_folder('test/fixtures/data/out-1.zip', 'test')





def test_build_datasets():
    _setup_test()
    client = OpenAIMockService("Test")
    creator = PracticeSkillChallengeCreator("Ruby on Rails", client, OUTPUT_PATH)

    course = MASTER_OUTLINE['courses']['working-with-databases-in-rails']
    prompt = creator.prepare_chapter_content_prompt(course)
    assert isinstance(prompt, str) == True


def test_build_prompt():
    _setup_test()
    client = OpenAIMockService("Test")
    creator = PracticeSkillChallengeCreator("Ruby on Rails", client, OUTPUT_PATH)

    course = MASTER_OUTLINE['courses']['working-with-databases-in-rails']
    prompt = creator.build_skill_challenge_prompt(course)
    assert len(prompt) == 2

    # Count tokens
    # The model returns 4096 tokens and we don't want to overrun the context window.
    max_tokens = 16385 - 4096
    prompt_string = str(prompt)
    characters = len(prompt_string)
    tokens = characters / 4  # => 9298.0

    assert tokens < max_tokens


def test_create_practice_skill_challenges():
    _setup_test()

    topics = ['Ruby on Rails']
    for topic in topics:
        session_name = f"{topic} Practice Skill Challenge"
        ai_client = OpenAIMockService(session_name)

        creator = PracticeSkillChallengeCreator(topic, ai_client, OUTPUT_PATH)
        outline = creator.create_practice_skill_challenges_for_chapters()

        for course_data in outline['courses'].values():
            for chapter_data in course_data['chapters'].values():
                paths = chapter_data['paths']
                page_names = [p.split('/')[-1] for p in paths]
                challenge_pages = [p for p in page_names if 'challenge' in p]
                assert len(challenge_pages) == 2
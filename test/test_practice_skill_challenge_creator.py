from src.utils.files import read_json_file, unzip_folder, scan_directory
from src.openai.practice_skill_challenge_creator import PracticeSkillChallengeCreator
from .mocks.openai_mock_service import OpenAIMockService
import os
import shutil

OUTPUT_PATH = "test/out"
MASTER_OUTLINE = read_json_file("test/fixtures/data/master-outline-2.json")

# Setup output folder
slug = 'ruby-on-rails'
if (os.path.exists(f"{OUTPUT_PATH}/{slug}")):
    shutil.rmtree(f"{OUTPUT_PATH}/{slug}")
unzip_folder('test/fixtures/data/out-1.zip', 'test')

client = OpenAIMockService("Test")
creator = PracticeSkillChallengeCreator("Ruby on Rails", client, OUTPUT_PATH)


def test_build_datasets():
    course = MASTER_OUTLINE['courses']['ruby-fundamentals']
    prompt = creator.prepare_datasets(course)
    assert len(prompt) == 20


def test_build_prompt():
    course = MASTER_OUTLINE['courses']['ruby-fundamentals']
    prompt = creator.build_skill_challenge_prompt(course)
    assert len(prompt) == 22

    # Count tokens
    # The model returns 4096 tokens and we don't want to overrun the context window.
    max_tokens = 16385 - 4096
    prompt_string = str(prompt)
    characters = len(prompt_string)
    tokens = characters / 4  # => 11650

    assert tokens < max_tokens


def test_create_practice_skill_challenges():
    topics = ['Ruby on Rails']
    for topic in topics:
        session_name = f"{topic} Practice Skill Challenge"
        ai_client = OpenAIMockService(session_name)

        creator = PracticeSkillChallengeCreator(topic, ai_client, OUTPUT_PATH)
        outline = creator.create_practice_skill_challenges_for_chapters()

        for _course_slug, course_data in outline['courses'].items():
            for _chapter_slug, chapter_data in course_data['chapters'].items():
                paths = chapter_data['paths']
                page_names = [p.split('/')[-1] for p in paths]
                challenge_pages = [p for p in page_names if 'challenge' in p]
                assert len(challenge_pages) == 1
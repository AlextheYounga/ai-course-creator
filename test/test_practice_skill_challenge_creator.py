import shutil
import os
from src.utils.strings import slugify
from src.utils.files import read_yaml_file, unzip_folder
from src.creator.challenges.practice_skill_challenge_creator import PracticeSkillChallengeCreator
from .mocks.openai_mock_service import OpenAIMockService
from .mocks.db import *



MASTER_OUTLINE = 'test/fixtures/data/master-outline.yaml'
OUTPUT_PATH = "test/out"


def _setup_test():
    truncate_tables()

    slug = 'ruby-on-rails'

    if (os.path.exists(f"{OUTPUT_PATH}/{slug}")):
        shutil.rmtree(f"{OUTPUT_PATH}/{slug}")
    unzip_folder('test/fixtures/data/out.zip', 'test')

    # Instantiate db records
    topic_record = Topic(name="Ruby on Rails", slug="ruby-on-rails")
    DB.add(topic_record)
    DB.commit()

    # Import outline
    Outline.get_or_create_from_file(DB, topic_record.id, MASTER_OUTLINE)


def test_build_datasets():
    _setup_test()
    master_outline = read_yaml_file(MASTER_OUTLINE)

    client = OpenAIMockService("Test")
    creator = PracticeSkillChallengeCreator("Ruby on Rails", client)

    course_slug = slugify(master_outline[1]['course']['courseName'])
    chapter_slug = slugify(master_outline[1]['course']['chapters'][0]['name'])

    prompt = creator.prepare_chapter_content_prompt(course_slug, chapter_slug)
    assert isinstance(prompt, str) == True


def test_build_prompt():
    _setup_test()
    master_outline = read_yaml_file(MASTER_OUTLINE)

    client = OpenAIMockService("Test")
    creator = PracticeSkillChallengeCreator("Ruby on Rails", client)

    course_slug = slugify(master_outline[1]['course']['courseName'])
    chapter_slug = slugify(master_outline[1]['course']['chapters'][0]['name'])

    prompt = creator.build_skill_challenge_prompt(course_slug, chapter_slug)
    assert len(prompt) == 2

    # Count tokens
    # The model returns 4096 tokens and we don't want to overrun the context window.
    max_tokens = 16385 - 4096
    prompt_string = str(prompt)
    characters = len(prompt_string)
    tokens = characters / 4

    assert tokens < max_tokens


def test_create_practice_skill_challenges():
    _setup_test()
    topic = 'Ruby on Rails'

    client = OpenAIMockService(f"{topic} Practice Skill Challenge")
    creator = PracticeSkillChallengeCreator(topic, client)
    practice_pages = creator.create_from_outline()

    # Checking output
    for page in practice_pages:
        if page.type == 'challenge':
            assert page != None
            assert page.content != None
            assert page.generated == True

import shutil
import os
from src.utils.strings import slugify
from src.utils.files import read_yaml_file, unzip_folder
from src.creator.course_creator import CourseCreator
from src.creator.challenges.final_skill_challenge_creator import FinalSkillChallengeCreator
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
    topic_record = Topic.first_or_create(DB, "Ruby on Rails")

    # Import outline
    Outline.import_outline(DB, topic_record.id, MASTER_OUTLINE)


def test_build_datasets():
    _setup_test()

    master_outline = read_yaml_file(MASTER_OUTLINE)
    topic_record = DB.query(Topic).filter(Topic.name == "Ruby on Rails").first()

    client = OpenAIMockService("Test")
    creator = FinalSkillChallengeCreator(topic_record.id, client)

    course_slug = slugify(master_outline[1]['course']['courseName'])

    prompt = creator.prepare_course_content_prompt(course_slug)
    assert isinstance(prompt, str) == True


def test_build_prompt():
    _setup_test()

    master_outline = read_yaml_file(MASTER_OUTLINE)
    topic_record = DB.query(Topic).filter(Topic.name == "Ruby on Rails").first()

    client = OpenAIMockService("Test")
    creator = FinalSkillChallengeCreator(topic_record.id, client)

    course_slug = slugify(master_outline[1]['course']['courseName'])
    prompt = creator.build_skill_challenge_prompt(course_slug)
    assert len(prompt) == 2

    # Count tokens
    # The model returns 4096 tokens and we don't want to overrun the context window.
    max_tokens = 16385 - 4096
    prompt_string = str(prompt)
    characters = len(prompt_string)
    tokens = characters / 4  # => 9298.0

    assert tokens < max_tokens


def test_create_final_skill_challenges():
    _setup_test()
    topic = "Ruby on Rails"

    creator = CourseCreator(OpenAIMockService, topic)
    fsc_pages = creator.create_topic_final_skill_challenges()

    # Checking output
    for page in fsc_pages:
        assert page != None
        assert page.content != None
        assert page.generated == True

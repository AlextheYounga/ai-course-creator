import shutil
import os
from src.creator.course_creator import CourseCreator
from .mocks.openai_mock_service import OpenAIMockService
from .mocks.db import *



MASTER_OUTLINE = 'test/fixtures/data/master-outline.yaml'
OUTPUT_PATH = "test/out"


def _setup_test():
    truncate_tables()

    slug = 'ruby-on-rails'

    if (os.path.exists(f"{OUTPUT_PATH}/{slug}")):
        shutil.rmtree(f"{OUTPUT_PATH}/{slug}")

    os.makedirs(f"{OUTPUT_PATH}/{slug}", exist_ok=True)
    shutil.copy(MASTER_OUTLINE, f"{OUTPUT_PATH}/{slug}/master-outline.yaml")

    # Instantiate db records
    Topic.first_or_create(DB, "Ruby on Rails")


def test_create_page_material():
    _setup_test()

    topic = 'Ruby on Rails'
    creator = CourseCreator(OpenAIMockService, topic)
    pages = creator.create_topic_page_material()

    # Checking output
    for page in pages:
        if page.type == 'page':
            assert page != None
            assert page.content != None
            assert page.generated == True

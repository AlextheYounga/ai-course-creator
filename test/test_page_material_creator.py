import shutil
import os
from src.creator.pages.page_material_creator import PageMaterialCreator
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
    topic_record = Topic(name="Ruby on Rails", slug="ruby-on-rails")
    DB.add(topic_record)
    DB.commit()


def test_create_page_material():
    _setup_test()

    topic = 'Ruby on Rails'

    session_name = f"{topic} Test Page Material"
    ai_client = OpenAIMockService(session_name)

    creator = PageMaterialCreator(topic, ai_client)
    pages = creator.create_from_outline()

    # Checking output
    for page in pages:
        if page.type == 'page':
            assert page != None
            assert page.content != None
            assert page.generated == True

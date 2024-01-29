import shutil
import os
from src.creator.outlines.outline_creator import OutlineCreator
from src.creator.outlines.outline_processor import OutlineProcessor
from .mocks.openai_mock_service import OpenAIMockService
from .mocks.db import *
from src.utils.files import write_json_file



OUTPUT_PATH = "test/out"
TOPIC = 'Ruby on Rails'
SLUG = 'ruby-on-rails'
MASTER_OUTLINE = 'test/fixtures/data/master-outline.yaml'


def _setup_test():
    truncate_tables()

    # Reset output directory
    if (os.path.exists(f"{OUTPUT_PATH}/{SLUG}")):
        shutil.rmtree(f"{OUTPUT_PATH}/{SLUG}")

    os.makedirs(f"{OUTPUT_PATH}/{SLUG}", exist_ok=True)
    shutil.copy(MASTER_OUTLINE, f"{OUTPUT_PATH}/{SLUG}/master-outline.yaml")

    # Instantiate db records
    topic_record = Topic(name="Ruby on Rails", slug="ruby-on-rails")
    DB.add(topic_record)
    DB.commit()



_setup_test()


def test_hash_outline():
    outline_data = open(MASTER_OUTLINE).read()
    hash = OutlineProcessor.hash_outline(outline_data)
    assert hash != None

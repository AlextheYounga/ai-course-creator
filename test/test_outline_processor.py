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
MASTER_OUTLINE = 'test/out/ruby-on-rails/master-outline.yaml'


def _setup_test():
    # Reset output directory
    if (os.path.exists(f"{OUTPUT_PATH}/{SLUG}")):
        shutil.rmtree(f"{OUTPUT_PATH}/{SLUG}")

    session_name = f"{TOPIC} Outlines"
    ai_client = OpenAIMockService(session_name)

    creator = OutlineCreator(TOPIC, ai_client)
    creator.create()

_setup_test()

def test_hash_outline():
    outline_data = open(MASTER_OUTLINE).read()
    hash = OutlineProcessor.hash_outline(outline_data)
    assert hash == '055ca92ed89eba158cabc9466a2cbd42'


def test_get_outline_record_from_file():
    outline_record = OutlineProcessor.get_outline_record_from_file(MASTER_OUTLINE)
    assert outline_record.id == 1


def test_build_outline_rows():
    get_outline_metadata = OutlineProcessor.get_outline_metadata(1)
    write_json_file('test/rows.json', get_outline_metadata)


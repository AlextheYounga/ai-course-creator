import shutil
import os
from src.creator.outlines.outline_creator import OutlineCreator
from .mocks.openai_mock_service import OpenAIMockService
from .mocks.db import *
import yaml


OUTPUT_PATH = "test/out"


def _setup_test():
    # Nuke output folder
    slug = 'ruby-on-rails'
    if (os.path.exists(f"{OUTPUT_PATH}/{slug}")):
        shutil.rmtree(f"{OUTPUT_PATH}/{slug}")



_setup_test()


def test_create_outlines():
    truncate_tables()
    topic = 'Ruby on Rails'
    session_name = f"{topic} Outlines"
    ai_client = OpenAIMockService(session_name)

    # Create Outlines
    creator = OutlineCreator(topic, ai_client)
    outline_id = creator.create()

    outline = DB.get(Outline, outline_id)

    # Checking output
    assert outline_id == 1

    assert os.path.exists('test/out/ruby-on-rails/master-outline.yaml') == True
    assert len(outline.master_outline) == 7


def test_create_outlines_with_existing_outline():
    topic = 'Ruby on Rails'
    ai_client = OpenAIMockService(f"{topic} Outlines")

    outline_file = 'test/out/ruby-on-rails/master-outline.yaml'
    outline_data = yaml.safe_load(open(outline_file).read())
    outline_data[0]['course']['courseName'] = 'Ruby on Rails 2'

    with open(outline_file, 'w') as yaml_file:
        yaml.dump(outline_data, yaml_file, sort_keys=False)

    creator = OutlineCreator(topic, ai_client)
    outline_id = creator.create()

    outline = DB.get(Outline, outline_id)

    assert outline.id == 2
    assert len(outline.master_outline) == 7


def test_create_outlines_with_existing_outline_record_without_file():
    truncate_tables()
    _setup_test()

    topic = 'Ruby on Rails'
    ai_client = OpenAIMockService(f"{topic} Outlines")

    creator = OutlineCreator(topic, ai_client)
    outline_id = creator.create()

    outline_file = 'test/out/ruby-on-rails/master-outline.yaml'
    outline_data = yaml.safe_load(open(outline_file).read())
    outline_data[0]['course']['courseName'] = 'Ruby on Rails 2'

    with open(outline_file, 'w') as yaml_file:
        yaml.dump(outline_data, yaml_file, sort_keys=False)

    creator = OutlineCreator(topic, ai_client)
    outline_id = creator.create()

    outline = DB.get(Outline, outline_id)

    assert outline.id == 2
    assert len(outline.master_outline) == 7

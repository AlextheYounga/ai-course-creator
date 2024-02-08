import os
import shutil
from src.utils.files import read_yaml_file
from src.creator.outlines.master_outline_generator import MasterOutlineGenerator
from .mocks.openai_mock_service import OpenAIMockService
from .mocks.db import *



OUTPUT_PATH = "test/out"
REPLACE_KEYS = ["{topic}", "{skills}", "{page_name}"]
EXPECTED_MASTER_OUTLINE_RESPONSE = open('test/fixtures/responses/master-outline.md').read()
PARSED_SKILLS = read_yaml_file('test/fixtures/data/skills.yaml')



def _setup_test():
    truncate_tables()

    # Nuke output folder
    slug = 'ruby-on-rails'
    if (os.path.exists(f"{OUTPUT_PATH}/{slug}")):
        shutil.rmtree(f"{OUTPUT_PATH}/{slug}")

    # Instantiate db records
    topic_record = Topic.first_or_create(DB, "Ruby on Rails")

    outline = Outline.instantiate(DB, topic_record.id)
    outline.skills = PARSED_SKILLS
    DB.add(outline)
    DB.commit()

    return outline.id


def test_build_master_outline_prompt():
    outline_id = _setup_test()

    client = OpenAIMockService("Test")
    generator = MasterOutlineGenerator(outline_id, client)

    prompt = generator.build_master_outline_prompt()

    assert len(prompt) == 2

    system_prompt = prompt[0]['content']
    user_prompt = prompt[1]['content']

    for key in REPLACE_KEYS:
        assert key not in user_prompt
        assert key not in system_prompt


def test_generate_master_outline():
    outline_id = _setup_test()

    client = OpenAIMockService("Test")
    generator = MasterOutlineGenerator(outline_id, client)

    outline = generator.generate()

    assert len(outline.master_outline) == 7

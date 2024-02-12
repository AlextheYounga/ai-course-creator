import os
import shutil
from src.utils.files import read_yaml_file, read_json_file
from src.creator.outlines.master_outline_compiler import MasterOutlineCompiler
from .mocks.openai_mock_service import OpenAIMockService
from .mocks.db import *



OUTPUT_PATH = "test/out"
REPLACE_KEYS = ["{topic}", "{skills}", "{page_name}"]
OUTLINE_CHUNKS = read_json_file('test/fixtures/data/outline-chunks.json')
EXPECTED_MASTER_OUTLINE = read_yaml_file('test/fixtures/data/master-outline.yaml')
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
    outline.outline_chunks = OUTLINE_CHUNKS
    DB.add(outline)
    DB.commit()

    return outline.id


def test_generate_master_outline():
    outline_id = _setup_test()

    client = OpenAIMockService("Test")
    compiler = MasterOutlineCompiler(outline_id, client)
    outline = compiler.compile()

    assert outline.hash == Outline.hash_outline(EXPECTED_MASTER_OUTLINE)

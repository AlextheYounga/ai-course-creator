import os
import shutil
from src.utils.files import read_yaml_file
from src.creator.outlines.build_master_outline import MasterOutlineBuilder
from .mocks.openai_mock_service import OpenAIMockService
from .mocks.db import *



OUTPUT_PATH = "test/out"
REPLACE_KEYS = ["{topic}", "{draft_outline}", "{skills}", "{page_name}"]
EXPECTED_COURSE_OUTLINE_RESPONSE = open('test/fixtures/responses/course-outline.md').read()
PARSED_SKILLS = read_yaml_file('test/fixtures/data/skills.yaml')
PARSED_DRAFT_OUTLINE = read_yaml_file('test/fixtures/data/draft-outline.yaml')



def _setup_test():
    # Nuke output folder
    slug = 'ruby-on-rails'
    if (os.path.exists(f"{OUTPUT_PATH}/{slug}")):
        shutil.rmtree(f"{OUTPUT_PATH}/{slug}")

    # Instantiate db records
    topic_record = DB.query(Topic).filter(Topic.name == "Ruby on Rails").first()
    if not topic_record:
        # Save topic to database
        topic_record = Topic(name="Ruby on Rails", slug="ruby-on-rails")
        DB.add(topic_record)
        DB.commit()

        outline_record = Outline.instantiate(topic_record)
        outline_record.skills = PARSED_SKILLS
        outline_record.draft_outline = PARSED_DRAFT_OUTLINE
        DB.add(outline_record)
        DB.commit()

    outline_record = topic_record.outlines[0]

    return outline_record.id


def test_build_draft_prompt():
    outline_id = _setup_test()

    client = OpenAIMockService("Test")
    builder = MasterOutlineBuilder(outline_id, client)

    course_name = PARSED_DRAFT_OUTLINE[0]['courseName']
    modules = PARSED_DRAFT_OUTLINE[0]['modules']
    prompt = builder.build_optimize_outline_prompt(course_name, modules)

    system_prompt = prompt[0]['content']
    user_prompt = prompt[1]['content']

    assert len(prompt) == 2

    for key in REPLACE_KEYS:
        assert key not in user_prompt
        assert key not in system_prompt


def test_generate_master_outline():
    outline_id = _setup_test()

    client = OpenAIMockService("Test")
    builder = MasterOutlineBuilder(outline_id, client)

    master_outline = builder.generate()

    assert master_outline != None
    assert os.path.exists('test/out/ruby-on-rails/master-outline.yaml') == True

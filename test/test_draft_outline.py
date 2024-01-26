import os
import shutil
from src.utils.files import read_yaml_file
from src.creator.outlines.draft_outline import DraftOutline
from .mocks.openai_mock_service import OpenAIMockService
from .mocks.db import *



OUTPUT_PATH = "test/out"
REPLACE_KEYS = ["{topic}", "{draft_outline}", "{skills}", "{page_name}"]
EXPECTED_DRAFT_OUTLINE_RESPONSE = open('test/fixtures/responses/draft-outline.md').read()
PARSED_SKILLS = read_yaml_file('test/fixtures/data/skills.yaml')



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
        DB.add(outline_record)
        DB.commit()

    outline_record = topic_record.outlines[0]

    return outline_record.id


def test_build_draft_prompt():
    outline_id = _setup_test()

    client = OpenAIMockService("Test")
    draft = DraftOutline(outline_id, client)

    prompt = draft.build_draft_prompt()

    assert len(prompt) == 2

    system_prompt = prompt[0]['content']
    user_prompt = prompt[1]['content']

    for key in REPLACE_KEYS:
        assert key not in user_prompt
        assert key not in system_prompt


def test_generate_draft_outline():
    outline_id = _setup_test()

    client = OpenAIMockService("Test")
    draft = DraftOutline(outline_id, client)

    draft_outline = draft.generate()

    assert draft_outline['valid'] == True

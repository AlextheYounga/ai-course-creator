import shutil
import os
from src.utils.files import read_yaml_file
from src.creator.outlines.outline_processor import OutlineProcessor
from src.creator.pages.page_material_creator import PageMaterialCreator
from .mocks.openai_mock_service import OpenAIMockService
from .mocks.db import *


DB = setup_db()
MASTER_OUTLINE = 'test/fixtures/data/master-outline.yaml'
OUTPUT_PATH = "test/out"


def _setup_test():
    slug = 'ruby-on-rails'

    if (os.path.exists(f"{OUTPUT_PATH}/{slug}")):
        shutil.rmtree(f"{OUTPUT_PATH}/{slug}")

    os.makedirs(f"{OUTPUT_PATH}/{slug}", exist_ok=True)
    shutil.copy(MASTER_OUTLINE, f"{OUTPUT_PATH}/{slug}/master-outline.yaml")

    # Instantiate db records
    topic_record = Topic(name="Ruby on Rails", slug="ruby-on-rails")
    DB.add(topic_record)
    DB.commit()

    outline_record = Outline.instantiate(topic_record)
    outline_record.master_outline = read_yaml_file(MASTER_OUTLINE)
    outline_record.hash = OutlineProcessor.hash_outline(outline_record.master_outline)
    DB.add(outline_record)
    DB.commit()


def test_create_page_material():
    _setup_test()

    topic = 'Ruby on Rails'
    session_name = f"{topic} Page Material"

    ai_client = OpenAIMockService(session_name)

    creator = PageMaterialCreator(topic, ai_client)
    outline_rows = creator.create_practice_skill_challenges_for_chapters()

    for row in outline_rows:
        if row['type'] == 'page':

            page_record = DB.query(Page).filter(
                Page.course_slug == row['courseSlug'],
                Page.chapter_slug == row['chapterSlug'],
                Page.slug == row['slug']
            ).first()

            assert page_record != None
            assert page_record.content != None
            assert page_record.generated == True

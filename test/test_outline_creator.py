import shutil
import os
from src.creator.course_creator import CourseCreator
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


def test_create_outline():
    truncate_tables()
    topic = 'Ruby on Rails'

    creator = CourseCreator(OpenAIMockService, topic)
    outline_id = creator.create_outline()

    # Checking output
    assert outline_id == 1

    outline = DB.get(Outline, outline_id)

    assert os.path.exists('test/out/ruby-on-rails/master-outline.yaml') == True
    assert len(outline.master_outline) == 7

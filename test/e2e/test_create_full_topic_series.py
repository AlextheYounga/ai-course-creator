import shutil
import os
from ..mocks.openai_mock_service import OpenAIMockService
from ..mocks.db import *
from src.creator.course_creator import CourseCreator


OUTPUT_PATH = "test/out"


def _setup_test():
    truncate_tables()

    # Reset output directory
    if (os.path.exists(f"{OUTPUT_PATH}")):
        shutil.rmtree(f"{OUTPUT_PATH}")



def test_create_full_course():
    _setup_test()

    topic = 'Ruby on Rails'

    creator = CourseCreator(OpenAIMockService, topic)

    # Begin creating course outlines
    outline_id = creator.create_outline()

    # Checking output
    assert outline_id == 1

    # Begin creating page material
    pages = creator.create_topic_page_material()

    # Checking output
    for page in pages:
        if page.type == 'page':
            assert page != None
            assert page.content != None
            assert page.generated == True

    # Begin creating practice skill challenges
    practice_pages = creator.create_topic_practice_skill_challenges()

    # Checking output
    for page in practice_pages:
        if page.type == 'challenge':
            assert page != None
            assert page.content != None
            assert page.generated == True

    # Begin creating final skill challenges
    fsc_pages = creator.create_topic_final_skill_challenges()

    # Checking output
    for page in fsc_pages:
        assert page != None
        assert page.content != None
        assert page.generated == True

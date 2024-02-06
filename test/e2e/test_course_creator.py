import shutil
import os
from ..mocks.openai_mock_service import OpenAIMockService
from ..mocks.db import *
from src.utils.files import unzip_folder
from src.creator.course_creator import CourseCreator


OUTPUT_PATH = "test/out"
MASTER_OUTLINE = 'test/fixtures/data/master-outline.yaml'


def _setup_test():
    truncate_tables()

    # Reset output directory
    if (os.path.exists(f"{OUTPUT_PATH}")):
        shutil.rmtree(f"{OUTPUT_PATH}")


def test_generate_course_material():
    _setup_test()
    unzip_folder('test/fixtures/data/out.zip', 'test')

    # Instantiate db records
    topic = Topic.first_or_create(DB, "Ruby on Rails")

    # Import outline
    Outline.process_outline(DB, topic.id, MASTER_OUTLINE)

    course = DB.query(Course).first()

    creator = CourseCreator(OpenAIMockService, topic.name)
    creator.generate_course(course)


def test_generate_chapter_material():
    _setup_test()
    unzip_folder('test/fixtures/data/out.zip', 'test')

    # Instantiate db records
    topic = Topic.first_or_create(DB, "Ruby on Rails")

    # Import outline
    Outline.process_outline(DB, topic.id, MASTER_OUTLINE)

    chapter = DB.query(Chapter).first()

    creator = CourseCreator(OpenAIMockService, topic.name)
    creator.generate_chapter(chapter)


def test_generate_course_final_skill_challenge():
    _setup_test()
    unzip_folder('test/fixtures/data/out.zip', 'test')

    # Instantiate db records
    topic = Topic.first_or_create(DB, "Ruby on Rails")

    # Import outline
    Outline.process_outline(DB, topic.id, MASTER_OUTLINE)

    course = DB.query(Course).first()

    creator = CourseCreator(OpenAIMockService, topic.name)
    creator.generate_course_final_skill_challenge(course)


def test_dynamic_generate_page_material_generate_course():
    _setup_test()
    unzip_folder('test/fixtures/data/out.zip', 'test')

    # Instantiate db records
    topic = Topic.first_or_create(DB, "Ruby on Rails")

    # Import outline
    Outline.process_outline(DB, topic.id, MASTER_OUTLINE)

    course = DB.query(Course).first()

    creator = CourseCreator(OpenAIMockService, topic.name)
    creator.generate_entity_page_material(course)

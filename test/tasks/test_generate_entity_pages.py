from ..mocks.db import *
from src.tasks.generate_pages_from_outline_entity import GeneratePagesFromOutlineEntity
from src.handlers.create_new_thread_handler import CreateNewThreadHandler
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
from src.handlers.outlines.create_new_outline_handler import CreateNewOutlineHandler


TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()


def __setup_test():
    truncate_tables()
    thread = CreateNewThreadHandler({'eventName': 'TestGenerateEntityPages'}).handle()
    topics_file = "storage/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()
    CreateNewOutlineHandler({'threadId': thread.id, 'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()


def test_generate_chapter_entity_pages():
    __setup_test()

    outline_entity = DB.query(OutlineEntity).filter(OutlineEntity.entity_type == 'Chapter').first()

    task = GeneratePagesFromOutlineEntity(topic_id=1, outline_entity_id=outline_entity.id)

    task.run()


def test_generate_course_entity_pages():
    __setup_test()

    outline_entity = DB.query(OutlineEntity).filter(OutlineEntity.entity_type == 'Course').first()

    task = GeneratePagesFromOutlineEntity(topic_id=1, outline_entity_id=outline_entity.id)

    task.run()


def test_generate_chapter_with_existing_entity_pages():
    outline_entity = DB.query(OutlineEntity).filter(OutlineEntity.entity_type == 'Chapter').first()

    task = GeneratePagesFromOutlineEntity(topic_id=1, outline_entity_id=outline_entity.id)

    task.run()

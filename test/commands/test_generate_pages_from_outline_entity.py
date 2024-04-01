from ..mocks.db import *
from src.commands.generate_pages_from_outline_entity import GeneratePagesFromOutlineEntity
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
from src.handlers.outlines.create_new_outline_handler import CreateNewOutlineHandler


TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()


def __setup_test():
    truncate_tables()
    thread = Thread.start(DB, __name__)
    topics_file = "storage/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()
    CreateNewOutlineHandler({'threadId': thread.id, 'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()


def test_generate_chapter_entity_pages():
    __setup_test()

    outline_entity = DB.query(OutlineEntity).filter(OutlineEntity.entity_type == 'Chapter').first()
    task = GeneratePagesFromOutlineEntity(topic_id=1, outline_entity_id=outline_entity.id, progress_bar=False)
    task.run()

    generated_pages = DB.query(Page).filter(Page.generated == True).all()

    assert len(generated_pages) == 5



def test_generate_course_entity_pages():
    __setup_test()

    outline_entity = DB.query(OutlineEntity).filter(OutlineEntity.entity_type == 'Course').first()
    course_count = DB.query(Page).filter(Page.course_id == outline_entity.entity_id).count()
    print(course_count)

    task = GeneratePagesFromOutlineEntity(topic_id=1, outline_entity_id=outline_entity.id, progress_bar=False)
    task.run()

    generated_pages = DB.query(Page).filter(Page.generated == True).all()

    assert len(generated_pages) == 10


def test_generate_course_entity_lesson_pages():
    __setup_test()

    outline_entity = DB.query(OutlineEntity).filter(OutlineEntity.entity_type == 'Course').first()
    course_count = DB.query(Page).filter(Page.course_id == outline_entity.entity_id).count()
    print(course_count)

    task = GeneratePagesFromOutlineEntity(
        topic_id=1,
        outline_entity_id=outline_entity.id,
        page_type='lesson',
        progress_bar=False
    )

    task.run()

    generated_pages = DB.query(Page).filter(Page.generated == True).all()

    assert len(generated_pages) == 7

    for page in generated_pages:
        assert page.type == 'lesson'


# def test_generate_chapter_with_existing_entity_pages():
#     outline_entity = DB.query(OutlineEntity).filter(OutlineEntity.entity_type == 'Chapter').first()
#     task = GeneratePagesFromOutlineEntity(topic_id=1, outline_entity_id=outline_entity.id, progress_bar=False)
#     task.run()

#     generated_pages = DB.query(Page).filter(
#         Page.generated == True,
#         Page.active == True
#     ).all()

#     soft_deleted_pages = DB.query(Page).filter(Page.id.in_([1, 2, 3, 4, 5])).all()

#     assert len(generated_pages) == 10
#     assert len(soft_deleted_pages) == 5

#     for page in generated_pages:
#         assert page.active == True
#         assert page.generated == True

#     for page in soft_deleted_pages:
#         assert page.active == False
#         assert page.generated == True

from .mocks.mock_db import *
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker
from src.handlers import CreateNewOutlineHandler
from src.events.events import GeneratePagesFromOutlineJobRequested

TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()


def __setup_test():
    truncate_tables()  # Delete all data from the tables
    import_sql_from_file(DB_PATH, 'test/fixtures/sql/topic.sql')
    CreateNewOutlineHandler({'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()


def __run_job(data: dict):
    queue_context = QueueContext(monitor_progress=True)
    storage_queue = StorageQueue()
    job_queue = JobQueue(storage_queue, 'main_queue')
    job_event = GeneratePagesFromOutlineJobRequested(data)
    job = Job({'data': job_event.serialize()})
    job_queue.enqueue(job)
    worker = Worker(queue_context, storage_queue, job_queue)
    worker.perform()


def test_generate_page_entity_job():
    __setup_test()
    db = get_session()

    outline_entity = db.query(OutlineEntity).filter(OutlineEntity.entity_type == 'Page').first()

    job_data = {
        'topicId': 1,
        'outlineId': 1,
        'outlineEntityId': outline_entity.id,
        'hasInteractives': False,
    }

    __run_job(job_data)

    generated_pages = db.query(Page).filter(Page.generated == True).all()
    assert len(generated_pages) == 1
    for page in generated_pages:
        assert page.course_id == outline_entity.entity_id



def test_generate_chapter_entity_pages_job():
    __setup_test()

    db = get_session()
    outline_entity = db.query(OutlineEntity).filter(OutlineEntity.entity_type == 'Chapter').first()

    job_data = {
        'topicId': 1,
        'outlineId': 1,
        'outlineEntityId': outline_entity.id
    }
    __run_job(job_data)

    generated_pages = db.query(Page).filter(Page.generated == True).all()

    for page in generated_pages:
        match page.type:
            case 'lesson':
                assert page.topic_id == 1
                assert page.chapter_id is not None
                assert page.course_id == outline_entity.entity_id
                assert page.content is not None
                assert page.content != ''
                assert page.generated
                assert page.hash is not None
            case 'challenge':
                assert page.topic_id == 1
                assert page.chapter_id is not None
                assert page.course_id == outline_entity.entity_id
            case 'final-skill-challenge':
                assert page.topic_id == 1
                assert page.chapter_id is not None
                assert page.course_id == outline_entity.entity_id

    assert len(generated_pages) == 4



def test_generate_course_entity_pages_job():
    __setup_test()
    db = get_session()
    outline_entity = db.query(OutlineEntity).filter(OutlineEntity.entity_type == 'Course').first()

    job_data = {
        'topicId': 1,
        'outlineId': 1,
        'outlineEntityId': outline_entity.id
    }

    __run_job(job_data)

    generated_pages = db.query(Page).filter(Page.generated == True).all()

    for page in generated_pages:
        match page.type:
            case 'lesson':
                assert page.topic_id == 1
                assert page.chapter_id is not None
                assert page.course_id == outline_entity.entity_id
                assert page.content is not None
                assert page.content != ''
                assert page.generated
                assert page.hash is not None
            case 'challenge':
                assert page.topic_id == 1
                assert page.chapter_id is not None
                assert page.course_id == outline_entity.entity_id
            case 'final-skill-challenge':
                assert page.topic_id == 1
                assert page.chapter_id is not None
                assert page.course_id == outline_entity.entity_id

    assert len(generated_pages) == 7

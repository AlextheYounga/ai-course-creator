from datetime import datetime
from .mocks.mock_db import *
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker
from src.handlers import ScanTopicsFileHandler, CreateNewOutlineHandler
from src.events.events import GeneratePagesFromOutlineJobRequested



TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()


def __setup_test():
    truncate_tables()  # Delete all data from the tables
    topics_file = "configs/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()
    CreateNewOutlineHandler({'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()


def __run_job(data: dict):
    queue_context = QueueContext(monitor_progress=True)
    storage_queue = StorageQueue()
    job_queue = JobQueue(storage_queue, 'main_queue')

    job_event = GeneratePagesFromOutlineJobRequested(data)
    job = Job({'data': job_event.serialize()})
    job_queue.enqueue(job)

    worker = Worker(queue_context, storage_queue, job_queue)

    worker = Worker(queue_context, storage_queue, job_queue)
    worker.perform()


def test_generate_page_entity_without_interactives_job():
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
    generated_interactives = db.query(Interactive).all()

    for page in generated_pages:
        assert page.course_id == outline_entity.entity_id
        assert page.interactive_ids is None

    assert len(generated_interactives) == 0
    assert len(generated_pages) == 1


def test_generate_page_entity_job():
    __setup_test()
    db = get_session()

    outline_entity = db.query(OutlineEntity).filter(OutlineEntity.entity_type == 'Page').first()

    job_data = {
        'topicId': 1,
        'outlineId': 1,
        'outlineEntityId': outline_entity.id
    }

    __run_job(job_data)

    generated_pages = db.query(Page).filter(Page.generated == True).all()

    for page in generated_pages:
        assert page.course_id == outline_entity.entity_id
        assert page.interactive_ids is not None

    assert len(generated_pages) == 1



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
        assert page.chapter_id == outline_entity.entity_id
        assert page.interactive_ids is not None

    assert len(generated_pages) == 5



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
        assert page.course_id == outline_entity.entity_id
        assert page.interactive_ids is not None

    assert len(generated_pages) == 10

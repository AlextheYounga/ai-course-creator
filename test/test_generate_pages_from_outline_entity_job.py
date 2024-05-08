from .mocks.mock_db import *
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker
from src.handlers import ScanTopicsFileHandler, CreateNewOutlineHandler
from src.events.events import GeneratePagesFromOutlineEntityRequested



TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()


def __setup_test():
    truncate_tables()  # Delete all data from the tables
    topics_file = "configs/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()
    CreateNewOutlineHandler({'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()


def __run_job(expected_jobs: int, data: dict):
    queue_context = QueueContext()
    storage_queue = StorageQueue()
    job_queue = JobQueue(storage_queue, 'main_queue')

    job_event = GeneratePagesFromOutlineEntityRequested(data)
    job = Job({'data': job_event.serialize()})
    job_queue.enqueue(job)

    worker = Worker(queue_context, storage_queue, job_queue)
    while expected_jobs > 0:
        worker.handle()
        expected_jobs -= 1


def test_generate_chapter_entity_pages_job():
    __setup_test()

    outline_entity = DB.query(OutlineEntity).filter(OutlineEntity.entity_type == 'Chapter').first()

    expected_jobs = 26
    job_data = {
        'topicId': 1,
        'outlineId': 1,
        'outlineEntityId': outline_entity.id
    }
    __run_job(expected_jobs, job_data)

    generated_pages = DB.query(Page).filter(Page.generated == True).all()

    for page in generated_pages:
        assert page.chapter_id == outline_entity.entity_id

    assert len(generated_pages) == 5



def test_generate_course_entity_pages_job():
    __setup_test()

    outline_entity = DB.query(OutlineEntity).filter(OutlineEntity.entity_type == 'Course').first()

    expected_jobs = 49
    job_data = {
        'topicId': 1,
        'outlineId': 1,
        'outlineEntityId': outline_entity.id
    }

    __run_job(expected_jobs, job_data)

    generated_pages = DB.query(Page).filter(Page.generated == True).all()

    for page in generated_pages:
        assert page.course_id == outline_entity.entity_id

    assert len(generated_pages) == 10


def test_generate_course_entity_lesson_pages_job():
    __setup_test()

    outline_entity = DB.query(OutlineEntity).filter(OutlineEntity.entity_type == 'Course').first()

    expected_jobs = 37
    job_data = {
        'threadId': 1,
        'topicId': 1,
        'pageType': 'lesson',
        'outlineId': 1,
        'outlineEntityId': outline_entity.id
    }

    __run_job(expected_jobs, job_data)

    generated_pages = DB.query(Page).filter(Page.generated == True).all()

    for page in generated_pages:
        assert page.course_id == outline_entity.entity_id

    assert len(generated_pages) == 7

    for page in generated_pages:
        assert page.type == 'lesson'

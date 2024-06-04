from .mocks.mock_db import *
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
from src.handlers.create_new_outline_handler import CreateNewOutlineHandler
from src.events.events import GeneratePageInteractivesJobRequested

TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()
PAGE_MATERIAL = open('test/fixtures/responses/page.md').read()


def __setup_test():
    truncate_tables()
    db = get_session()
    topics_file = "configs/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()
    CreateNewOutlineHandler({'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()

    page = db.get(Page, 1)
    content_hash = Page.hash_page(PAGE_MATERIAL)
    page.content = PAGE_MATERIAL
    page.hash = content_hash
    page.generated = True
    db.commit()


def __run_job(data: dict):
    queue_context = QueueContext()
    storage_queue = StorageQueue()
    job_queue = JobQueue(storage_queue, 'main_queue')

    job_event = GeneratePageInteractivesJobRequested(data)
    job = Job({'data': job_event.serialize()})
    job_queue.enqueue(job)

    worker = Worker(queue_context, storage_queue, job_queue)
    worker.perform()


def test_generate_page_interactives_process():
    __setup_test()

    db = get_session()

    job_data = {
        'topicId': 1,
        'outlineId': 1,
        'pageId': 1,
    }
    __run_job(job_data)

    generated_interactives = db.query(Interactive).all()

    assert len(generated_interactives) <= 10

from ..mocks.mock_db import *
from src.handlers.get_next_page_to_generate_from_job_handler import GetNextPageToGenerateFromJobHandler
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
from src.handlers.create_new_outline_handler import CreateNewOutlineHandler
from src.events.events import GeneratePagesFromOutlineJobRequested
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker


TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()
JOB_ID = 'clwzm7i9e001s4wepcoktrgqk'


def __run_partial_job(steps, data: dict):
    queue_context = QueueContext()
    storage_queue = StorageQueue()
    job_queue = JobQueue(storage_queue, 'main_queue')

    job_event = GeneratePagesFromOutlineJobRequested(data)
    job = Job({'id': JOB_ID, 'data': job_event.serialize()})
    job_queue.enqueue(job)

    worker = Worker(queue_context, storage_queue, job_queue)
    while steps > 0:
        worker.handle()
        steps -= 1

    worker.job_queue.queue.flush_all()  # Will leak more dispatched events if not flushed
    return job


def __setup_test():
    truncate_tables()
    topics_file = "configs/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()
    CreateNewOutlineHandler({'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()



def test_get_next_page_to_generate_from_thread_using_only_outline_id():
    __setup_test()

    job_data = {
        'topicId': 1,
        'outlineId': 1,
        'hasInteractives': False
    }
    __run_partial_job(20, job_data)

    triggered_event = GetNextPageToGenerateFromJobHandler({
        'jobId': JOB_ID,
        'outlineId': 1,
        'topicId': 1
    }).handle()

    assert triggered_event is not None
    assert triggered_event.data.get('pageId', None) is not None
    assert triggered_event.data['pageId'] == 4
    assert triggered_event.data.get('totalJobItems', None) == 54
    assert triggered_event.__class__.__name__ == 'GenerateLessonPageProcessStarted'



def test_get_next_page_to_generate_from_thread_using_chapter_outline_entity_id():
    __setup_test()

    job_data = {
        'topicId': 1,
        'outlineId': 1,
        'outlineEntityId': 6,
        'hasInteractives': False
    }
    __run_partial_job(10, job_data)

    triggered_event = GetNextPageToGenerateFromJobHandler({
        'outlineEntityId': 6,
        'jobId': JOB_ID,
        'outlineId': 1,
        'topicId': 1
    }).handle()

    assert triggered_event is not None
    assert triggered_event.data.get('pageId', None) is not None
    assert triggered_event.data['pageId'] == 2
    assert triggered_event.data.get('totalJobItems', None) == 4
    assert triggered_event.__class__.__name__ == 'GenerateLessonPageProcessStarted'

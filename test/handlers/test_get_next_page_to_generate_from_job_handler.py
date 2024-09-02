from ..mocks.mock_db import *
from src.handlers.get_next_page_to_generate_handler import GetNextPageToGenerateHandler
from src.handlers.create_new_outline_handler import CreateNewOutlineHandler
from src.events.events import GeneratePagesFromOutlineJobRequested
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker


TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()
JOB_ID = 'clwzm7i9e001s4wepcoktrgqk'


def __run_partial_job(steps, data: dict):
    queue_context = QueueContext(monitor_progress=True)
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
    import_sql_from_file(DB_PATH, 'test/fixtures/sql/topic.sql')
    CreateNewOutlineHandler({'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()



def test_get_next_page_to_generate_from_thread_using_only_outline_id():
    __setup_test()

    db = get_session()

    job_data = {
        'topicId': 1,
        'outlineId': 1,
        'hasInteractives': False
    }

    __run_partial_job(6, job_data)

    last_event = db.query(EventStore).order_by(EventStore.id.desc()).first()

    triggered_event = GetNextPageToGenerateHandler(last_event.data).handle()

    assert triggered_event is not None
    assert triggered_event.data.get('pageId', None) is not None
    assert triggered_event.data['pageId'] == 2
    assert len(triggered_event.data['generationIds']) == 54
    assert triggered_event.data['generationType'] == 'FULL_OUTLINE'
    assert triggered_event.data['completedGenerationIds'] == [1]
    assert triggered_event.__class__.__name__ == 'GenerateLessonPageProcessStarted'



def test_get_next_page_to_generate_from_thread_using_chapter_outline_entity_id():
    __setup_test()

    db = get_session()

    job_data = {
        'topicId': 1,
        'outlineId': 1,
        'outlineEntityId': 6,
        'hasInteractives': False,
    }
    __run_partial_job(6, job_data)

    last_event = db.query(EventStore).order_by(EventStore.id.desc()).first()

    triggered_event = GetNextPageToGenerateHandler(last_event.data).handle()

    assert triggered_event is not None
    assert triggered_event.data.get('pageId', None) is not None
    assert triggered_event.data['pageId'] == 2
    assert triggered_event.data['generationIds'] == [1, 2, 3, 4]
    assert triggered_event.data['completedGenerationIds'] == [1]
    assert triggered_event.data['generationType'] == 'OUTLINE_ENTITY'
    assert triggered_event.__class__.__name__ == 'GenerateLessonPageProcessStarted'

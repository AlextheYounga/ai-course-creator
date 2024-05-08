from .mocks.mock_db import *
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker
from src.handlers import ScanTopicsFileHandler, CreateNewOutlineHandler
from src.events.events import GenerateOutlineMaterialRequested


TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()


def __setup_test():
    truncate_tables()
    topics_file = "configs/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()

    CreateNewOutlineHandler({
        'topicId': 1,
        'outlineData': OUTLINE_DATA
    }).handle()


def __run_job(expected_jobs: int, data: dict):
    queue_context = QueueContext()
    storage_queue = StorageQueue()
    job_queue = JobQueue(storage_queue, 'main_queue')

    job_event = GenerateOutlineMaterialRequested(data)
    job = Job({'data': job_event.serialize()})
    job_queue.enqueue(job)

    worker = Worker(queue_context, storage_queue, job_queue)

    while expected_jobs > 0:
        worker.handle()
        expected_jobs -= 1


    return job


def __setup_with_existing():
    truncate_tables()
    import_sql_data_from_file('test/data/test.db', 'test/data/test.sql.zip', zipped=True)

    fsc_pages = DB.query(Page).filter(Page.type == 'final-skill-challenge').all()
    for page in fsc_pages:
        page.generated = False
        page.content = None
        page.hash = None
    DB.commit()


def test_generate_pages_from_outline():
    __setup_test()

    good_events = [
        'LessonPageProcessedAndSummarizedSuccessfully',
        'PracticeChallengePageResponseProcessedSuccessfully',
        'FinalChallengePageResponseProcessedSuccessfully'
    ]

    bad_events = [
        'InvalidLessonPageResponseFromOpenAI',
        'InvalidPracticeChallengePageResponseFromOpenAI',
        'InvalidFinalChallengePageResponseFromOpenAI'
    ]

    expected_jobs = 364
    job_data = {
        'topicId': 1,
        'outlineId': 1,
    }

    job = __run_job(expected_jobs, job_data)

    pages = DB.query(Page).all()
    assert len(pages) == 77

    for page in pages:
        assert page.content is not None
        assert page.content != ''
        assert page.generated
        assert page.topic_id == 1
        assert page.type in ['lesson', 'challenge', 'final-skill-challenge']
        assert page.chapter_id is not None
        assert page.hash is not None

    good_events = DB.query(EventStore).filter(
        EventStore.name.in_(good_events),
        EventStore.job_id == job.id
    ).count()

    bad_events = DB.query(EventStore).filter(
        EventStore.name.in_(bad_events),
        EventStore.job_id == job.id
    ).count()

    assert good_events == 77
    assert bad_events == 0



# def test_generate_only_outline_fsc_pages():
#     __setup_with_existing()

#     expected_jobs = 30
#     job_data = {
#         'topicId': 1,
#         'outlineId': 1,
#         'pageType': 'final-skill-challenge'
#     }

#     job = __run_job(expected_jobs, job_data)

#     events = DB.query(EventStore).filter(
#         EventStore.name == 'FinalChallengePageResponseProcessedSuccessfully',
#         EventStore.job_id == job.id
#     ).all()

#     assert len(events) == 7

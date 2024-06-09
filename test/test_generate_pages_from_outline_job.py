from .mocks.mock_db import *
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker
from src.handlers import ScanTopicsFileHandler, CreateNewOutlineHandler
from src.events.events import GeneratePagesFromOutlineJobRequested, GeneratePageInteractivesJobRequested


TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()


def __setup_test():
    truncate_tables()
    topics_file = "configs/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()
    CreateNewOutlineHandler({'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()


def __run_job(job_event):
    queue_context = QueueContext(monitor_progress=True)
    storage_queue = StorageQueue()
    job_queue = JobQueue(storage_queue, 'main_queue')
    job = Job({'data': job_event.serialize()})
    job_queue.enqueue(job)
    worker = Worker(queue_context, storage_queue, job_queue)
    worker.perform()



def test_generate_pages_from_outline():
    __setup_test()

    db = get_session()

    good_events = [
        'LessonPageProcessedAndSummarizedSuccessfully',
    ]

    bad_events = [
        'InvalidLessonPageResponseFromOpenAI',
        "MultipleChoiceInteractiveShortcodeParsingFailed",
        "CodeEditorInteractiveShortcodeParsingFailed",
        "CodepenInteractiveShortcodeParsingFailed",
    ]

    job_data = {'topicId': 1, 'outlineId': 1}
    job_event = GeneratePagesFromOutlineJobRequested(job_data)
    __run_job(job_event)

    pages = db.query(Page).all()

    assert len(pages) == 77

    for page in pages:
        match page.type:
            case 'lesson':
                assert page.topic_id == 1
                assert page.chapter_id is not None
                assert page.content is not None
                assert page.content != ''
                assert page.generated
                assert page.hash is not None
            case 'challenge':
                assert page.topic_id == 1
                assert page.chapter_id is not None
            case 'final-skill-challenge':
                assert page.topic_id == 1
                assert page.chapter_id is not None


    good_events = db.query(EventStore).filter(
        EventStore.name.in_(good_events),
        EventStore.job_id == 1
    ).count()
    bad_events = db.query(EventStore).filter(
        EventStore.name.in_(bad_events),
        EventStore.job_id == 1
    ).count()

    assert good_events == 54
    assert bad_events == 0

import time
from .mocks.mock_db import *
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker
from src.handlers import ScanTopicsFileHandler, CreateNewOutlineHandler
from src.events.events import GeneratePagesFromOutlineJobRequested


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


def __run_job(data: dict):
    queue_context = QueueContext()
    storage_queue = StorageQueue()
    job_queue = JobQueue(storage_queue, 'main_queue')

    job_event = GeneratePagesFromOutlineJobRequested(data)
    job = Job({'data': job_event.serialize()})
    job_queue.enqueue(job)

    worker = Worker(queue_context, storage_queue, job_queue)

    worker = Worker(queue_context, storage_queue, job_queue)
    worker.perform()

    return job


def test_generate_pages_from_outline_without_interactives():
    __setup_test()

    db = get_session()

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

    job_data = {
        'topicId': 1,
        'outlineId': 1,
        'hasInteractives': False
    }

    job = __run_job(job_data)

    pages = db.query(Page).all()
    assert len(pages) == 77

    for page in pages:
        assert page.topic_id == 1
        assert page.chapter_id is not None
        assert page.type in ['lesson', 'challenge', 'final-skill-challenge']

        match page.type:
            case 'lesson':
                assert page.content is not None
                assert page.content != ''
                assert page.generated
                assert page.hash is not None
            case 'challenge':
                assert page.content is None
                assert page.generated is False
                assert page.hash is None
            case 'final-skill-challenge':
                assert page.content is None
                assert page.generated is False
                assert page.hash is None


    good_events = db.query(EventStore).filter(
        EventStore.name.in_(good_events),
        EventStore.job_id == job.id
    ).count()

    bad_events = db.query(EventStore).filter(
        EventStore.name.in_(bad_events),
        EventStore.job_id == job.id
    ).count()

    assert good_events == 54
    assert bad_events == 0


def test_generate_pages_from_outline_with_interactives():
    __setup_test()

    db = get_session()

    good_events = [
        'LessonPageProcessedAndSummarizedSuccessfully',
        'PracticeChallengePageResponseProcessedSuccessfully',
        'FinalChallengePageResponseProcessedSuccessfully'
    ]

    bad_events = [
        'InvalidLessonPageResponseFromOpenAI',
        'InvalidPracticeChallengePageResponseFromOpenAI',
        'InvalidFinalChallengePageResponseFromOpenAI'
        "MultipleChoiceInteractiveShortcodeParsingFailed",
        "CodeEditorInteractiveShortcodeParsingFailed",
        "CodepenInteractiveShortcodeParsingFailed",
    ]

    job_data = {
        'topicId': 1,
        'outlineId': 1,
    }

    job = __run_job(job_data)

    pages = db.query(Page).all()
    interactives = db.query(Interactive).all()

    assert len(pages) == 77
    assert len(interactives) > 0
    assert len(interactives) <= 385  # Highest possible number of interactives

    for page in pages:
        assert page.topic_id == 1
        assert page.chapter_id is not None
        assert page.type in ['lesson', 'challenge', 'final-skill-challenge']
        assert page.content is not None
        assert page.content != ''
        assert page.generated
        assert page.hash is not None
        assert len(page.interactive_ids) > 0

    for interactive in interactives:
        assert interactive.outline_entity_id is not None
        assert interactive.type in ['multipleChoice', 'codeEditor', 'codepen']
        assert interactive.difficulty in [1, 2, 3]
        assert interactive.data is not None
        assert interactive.data != ''

    good_events = db.query(EventStore).filter(
        EventStore.name.in_(good_events),
        EventStore.job_id == job.id
    ).count()

    bad_events = db.query(EventStore).filter(
        EventStore.name.in_(bad_events),
        EventStore.job_id == job.id
    ).count()

    assert good_events == 54
    assert bad_events == 0

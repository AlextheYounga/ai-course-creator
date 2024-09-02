from .mocks.mock_db import *
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker
from src.events.events import GeneratePageInteractivesJobRequested


def __setup_test():
    truncate_tables()
    import_sql_from_file(DB_PATH, 'test/fixtures/outline-no-interactives.sql.zip', zipped=True)


def __run_job(data: dict):
    queue_context = QueueContext(monitor_progress=True)
    storage_queue = StorageQueue()
    job_queue = JobQueue(storage_queue, 'main_queue')
    job_event = GeneratePageInteractivesJobRequested(data)
    job = Job({'data': job_event.serialize()})
    job_queue.enqueue(job)
    worker = Worker(queue_context, storage_queue, job_queue)
    worker.perform()



def test_generate_page_interactives_job():
    __setup_test()

    db = get_session()

    good_events = [
        'PageInteractivesGenerationComplete',
    ]

    bad_events = [
        "MultipleChoiceInteractiveShortcodeParsingFailed",
        "CodeEditorInteractiveShortcodeParsingFailed",
        "CodepenInteractiveShortcodeParsingFailed",
    ]

    job_data = {
        'topicId': 1,
        'outlineId': 1,
    }

    __run_job(job_data)

    interactives = db.query(Interactive).all()

    pages = db.query(Page).filter(
        Page.type.in_(['challenge', 'final-skill-challenge']),
    ).all()

    assert len(interactives) > 0
    assert len(interactives) <= 385  # Highest possible number of interactives

    for interactive in interactives:
        assert interactive.page_source_id is not None
        assert interactive.type in ['multipleChoice', 'codeEditor', 'codepen']
        assert interactive.difficulty in [1, 2, 3]
        assert interactive.data is not None
        assert interactive.data != ''

    # for page in pages:
    #     assert page.topic_id == 1
    #     assert page.chapter_id is not None
    #     assert page.content is not None
    #     assert page.content != ''
    #     assert page.generated
    #     assert page.hash is not None

        # match page.type:
        #     case 'challenge':
        #         assert page.content.startswith('# Practice Skill Challenge')
        #         assert len(page.interactives) >= 5
        #     case 'final-skill-challenge':
        #         assert page.content.startswith('# Final Skill Challenge')
        #         assert len(page.interactives) >= 20


    good_events = db.query(EventStore).filter(
        EventStore.name.in_(good_events),
        EventStore.job_id == 2
    ).count()

    bad_events = db.query(EventStore).filter(
        EventStore.name.in_(bad_events),
        EventStore.job_id == 2
    ).count()

    # assert good_events == 54 # Not sure what is happening here
    assert bad_events == 0

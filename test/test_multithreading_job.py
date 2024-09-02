import time
from .mocks.mock_db import *
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker
from src.handlers import CreateNewOutlineHandler
from src.events.events import GeneratePagesFromOutlineJobRequested

OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()


def __setup_test():
    truncate_tables()
    import_sql_from_file(DB_PATH, 'test/fixtures/sql/topic.sql')
    CreateNewOutlineHandler({'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()


def __jobs_finished(db):
    return db.query(EventStore).filter(EventStore.name == 'GenerateOutlinePagesJobFinished').count() == 2


def __run_job_async(data: dict):
    queue_context = QueueContext()
    storage_queue = StorageQueue()
    job_queue = JobQueue(storage_queue, 'main_queue')

    job_event = GeneratePagesFromOutlineJobRequested(data)
    job = Job({'data': job_event.serialize()})
    job_queue.enqueue(job)

    worker = Worker(queue_context, storage_queue, job_queue)
    worker.perform_async()

    return worker


def test_multithreading_queue():
    __setup_test()
    db = get_session()
    topic = db.query(Topic).first()
    topic_properties = topic.get_properties()
    topic_properties['settings']['hasInteractives'] = False
    topic.update_properties(DB, topic_properties)


    chapter_entities = db.query(OutlineEntity).filter(OutlineEntity.entity_type == 'Chapter').all()
    chapter_entity_1 = chapter_entities[0]
    chapter_entity_2 = chapter_entities[1]

    __run_job_async({'topicId': 1, 'outlineId': 1, 'outlineEntityId': chapter_entity_1.id})
    __run_job_async({'topicId': 1, 'outlineId': 1, 'outlineEntityId': chapter_entity_2.id})

    while not __jobs_finished(db):
        time.sleep(1)

    generated_pages = db.query(Page).filter(Page.generated == True).all()

    for p in generated_pages:
        assert p.chapter_id in [chapter_entity_1.entity_id, chapter_entity_2.entity_id]

    assert len(generated_pages) == 7

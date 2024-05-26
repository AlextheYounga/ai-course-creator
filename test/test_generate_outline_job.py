from .mocks.mock_db import *
from src.events.events import GenerateOutlineJobRequested
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker
from src.utils.files import read_yaml_file

TOPIC = 'Ruby on Rails'
OUTLINE_DATA = read_yaml_file('test/fixtures/master-outline.yaml')


def __setup_test():
    truncate_tables()
    topics_file = "configs/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()


def __run_job(data: dict):
    queue_context = QueueContext()
    storage_queue = StorageQueue()
    job_queue = JobQueue(storage_queue, 'main_queue')

    job_event = GenerateOutlineJobRequested(data)
    job = Job({'data': job_event.serialize()})
    job_queue.enqueue(job)

    worker = Worker(queue_context, storage_queue, job_queue)
    worker.perform()


def test_generate_outline_job():
    __setup_test()

    db = get_session()

    failed_events = [
        'InvalidGenerateSkillsResponseFromOpenAI',
        'InvalidOutlineChunkResponseFromOpenAI',
        'FailedToParseYamlFromOutlineChunkResponse'
    ]

    job_data = {'topicId': 1}


    __run_job(job_data)

    topic = db.get(Topic, 1)
    outline = db.get(Outline, 1)
    outline_entities_count = db.query(OutlineEntity).filter(OutlineEntity.outline_id == outline.id).count()

    bad_events = db.query(EventStore).filter(
        EventStore.job_id == 1,
        EventStore.name.in_(failed_events)
    ).all()

    db.refresh(topic)

    assert outline.id is not None
    assert outline.topic_id == topic.id
    assert outline.hash == Outline.hash_outline(OUTLINE_DATA)
    assert topic.master_outline_id == outline.id
    assert outline_entities_count == 107
    assert bad_events == []

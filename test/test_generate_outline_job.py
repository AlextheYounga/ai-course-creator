from .mocks.mock_db import *
from src.events.events import GenerateOutlineRequested
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker
from src.utils.files import read_yaml_file

TOPIC = 'Ruby on Rails'
OUTLINE_DATA = read_yaml_file('test/fixtures/master-outline.yaml')


def __setup_test():
    truncate_tables()
    topics_file = "configs/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()


def __run_job(expected_jobs: int, data: dict):
    queue_context = QueueContext()
    storage_queue = StorageQueue()
    job_queue = JobQueue(storage_queue, 'main_queue')

    job_event = GenerateOutlineRequested(data)
    job = Job({'data': job_event.serialize()})
    job_queue.enqueue(job)

    worker = Worker(queue_context, storage_queue, job_queue)

    while expected_jobs > 0:
        worker.handle()
        expected_jobs -= 1

    return job


def test_generate_outline_job():
    __setup_test()

    failed_events = [
        'InvalidGenerateSkillsResponseFromOpenAI',
        'InvalidOutlineChunkResponseFromOpenAI',
        'FailedToParseYamlFromOutlineChunkResponse'
    ]

    expected_jobs = 22
    job_data = {'topicId': 1}

    job = __run_job(expected_jobs, job_data)

    topic = DB.get(Topic, 1)
    outline = DB.get(Outline, 1)
    outline_entities_count = DB.query(OutlineEntity).filter(OutlineEntity.outline_id == outline.id).count()

    bad_events = DB.query(EventStore).filter(
        EventStore.job_id == job.id,
        EventStore.name.in_(failed_events)
    ).all()

    DB.refresh(topic)

    assert outline.id is not None
    assert outline.topic_id == topic.id
    assert outline.hash == Outline.hash_outline(OUTLINE_DATA)
    assert topic.master_outline_id == outline.id
    assert outline_entities_count == 107
    assert bad_events == []

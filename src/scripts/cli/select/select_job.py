import inquirer
import pydoc
import redis
from db.db import DB, Topic, EventStore
from .select_topic import select_topic
from .select_generate_content import select_generate_content
from .select_jobstore import select_jobstore
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker
from src.events.events import GenerateOutlineJobRequested, GeneratePagesFromOutlineJobRequested, GeneratePagesFromOutlineJobRequested

db = DB()


def _dispatch(job_event, job_id=None):
    queue_context = QueueContext(monitor_progress=True)
    storage_queue = StorageQueue()
    job_queue = JobQueue(storage_queue, 'main_queue')

    job_data = {'data': job_event.serialize()}
    if job_id:
        job_data['jobId'] = job_id

    job = Job(job_data)
    job_queue.enqueue(job)

    worker = Worker(queue_context, storage_queue, job_queue)
    worker.perform()


def _generate_outline(topic: Topic):
    redis.Redis().flushall()  # We should flush all here to avoid running previous jobs
    job_data = {'topicId': topic.id}
    job_event = GenerateOutlineJobRequested(job_data)
    return _dispatch(job_event)


def _generate_page_material(topic: Topic, has_interactives=True):
    redis.Redis().flushall()  # We should flush all here to avoid running previous jobs
    job_data = select_generate_content(topic)

    job_data['hasInteractives'] = has_interactives

    # Generate Outline Entities (specific sections from outline)
    if 'outlineEntityId' in job_data:
        job_event = GeneratePagesFromOutlineJobRequested(job_data)
        return _dispatch(job_event)

    # Generate Full Outline Material
    job_event = GeneratePagesFromOutlineJobRequested(job_data)
    return _dispatch(job_event)


def _resume_job():
    job = select_jobstore()
    last_event = db.query(EventStore).filter_by(job_id=job.id).order_by(EventStore.id.desc()).first()
    event = pydoc.locate(f'src.events.events.{last_event.name}')(last_event.data)
    _dispatch(event, job.job_id)


def select_job():
    topic_name = select_topic()
    topic = Topic.first_or_create(db, name=topic_name)

    base_tasks = [
        'Generate Outline',
        'Generate Page Material With Interactives',
        'Generate Page Material Only',
        'Generate Interactives',
        'Resume Job',
    ]

    tasks = [
        inquirer.List('task',
                      message="Select task",
                      choices=list(base_tasks)),
    ]

    choice = inquirer.prompt(tasks, raise_keyboard_interrupt=True)
    task = choice['task']

    match task:
        case 'Generate Outline':
            return _generate_outline(topic)
        case 'Generate Page Material With Interactives':
            return _generate_page_material(topic)
        case 'Generate Page Material Only':
            return _generate_page_material(topic, has_interactives=False)
        case 'Generate Interactives':
            print("Not implemented. Work in progress...")
            return
        case 'Resume Job':
            return _resume_job()

import inquirer
import pydoc
import redis
from db.db import DB, Topic, EventStore
from .select_topic import select_topic
from .select_generate_content import select_generate_content
from .select_jobstore import select_jobstore
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker
from src.events.events import GenerateOutlineRequested, GenerateOutlineMaterialRequested, GeneratePagesFromOutlineEntityRequested

db = DB()


def _dispatch(job_event):
    queue_context = QueueContext()
    storage_queue = StorageQueue()
    job_queue = JobQueue(storage_queue, 'main_queue')

    job = Job({'data': job_event.serialize()})
    job_queue.enqueue(job)

    worker = Worker(queue_context, storage_queue, job_queue)
    worker.perform()


def _generate_outline(topic: Topic):
    redis.Redis().flushall()  # We should flush all here to avoid running previous jobs
    job_data = {'topicId': topic.id}
    job_event = GenerateOutlineRequested(job_data)
    return _dispatch(job_event)


def _generate_content(topic: Topic):
    redis.Redis().flushall()  # We should flush all here to avoid running previous jobs
    job_data = select_generate_content(topic)

    # Generate Outline Entities (specific sections from outline)
    if 'outlineEntityId' in job_data:
        job_event = GeneratePagesFromOutlineEntityRequested(job_data)
        return _dispatch(job_event)

    # Generate Full Outline Material
    job_event = GenerateOutlineMaterialRequested(job_data)
    return _dispatch(job_event)


def _resume_job(topic: Topic):
    job = select_jobstore()
    last_event = EventStore.query.filter_by(job_id=job.id).all().last()
    event = pydoc.locate(f'src.events.events.{last_event.name}')(last_event.data)
    _dispatch(event)



def select_job():
    topic_name = select_topic()
    topic = Topic.first_or_create(db, name=topic_name)

    base_tasks = {
        'Generate Outline': _generate_outline,
        'Generate Content': _generate_content,
        'Resume Job': _resume_job
    }

    tasks = [
        inquirer.List('task',
                      message="Select task",
                      choices=list(base_tasks.keys())),
    ]

    choice = inquirer.prompt(tasks, raise_keyboard_interrupt=True)
    task = choice['task']
    task_function = base_tasks[task]

    # Dynamic function call
    task_function(topic)

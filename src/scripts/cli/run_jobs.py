import pydoc
import redis
from db.db import DB, Topic, EventStore
from .select.multi_select_generate_content import multi_select_generate_content
from .select.select_jobstore import select_jobstore
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker
from src.events.events import GenerateOutlineJobRequested, GeneratePagesFromOutlineJobRequested, GeneratePageInteractivesJobRequested

db = DB()



def dispatch(job_event, job_id=None):
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


def generate_outline(topic: Topic):
    redis.Redis().flushall()  # We should flush all here to avoid running previous jobs
    job_data = {'topicId': topic.id}
    job_event = GenerateOutlineJobRequested(job_data)
    return dispatch(job_event)


def generate_page_material(topic: Topic, has_interactives=True):
    redis.Redis().flushall()  # We should flush all here to avoid running previous jobs
    job_data_list = multi_select_generate_content(topic)
    job_count = len(job_data_list)
    print(f'Running {job_count} jobs')

    for job_data in job_data_list:
        job_event = GeneratePagesFromOutlineJobRequested(job_data)
        dispatch(job_event)

        if has_interactives:
            job_event = GeneratePageInteractivesJobRequested(job_data)
            dispatch(job_event)




def resume_job():
    redis.Redis().flushall()  # We should flush all here to avoid running previous jobs
    job = select_jobstore()
    last_event = db.query(EventStore).filter_by(job_id=job.id).order_by(EventStore.id.desc()).first()
    event = pydoc.locate(f'src.events.events.{last_event.name}')(last_event.data)
    dispatch(event, job.job_id)

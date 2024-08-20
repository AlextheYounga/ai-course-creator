import pydoc
import redis
from db.db import DB, Topic, EventStore, Outline, JobStore
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker
from src.events.events import GenerateOutlineJobRequested, GeneratePagesFromOutlineJobRequested, GeneratePageInteractivesJobRequested, CompileInteractivesToPagesJobRequested
from typing import TypedDict, Union, Literal, Optional

db = DB()


class JobParams(TypedDict):
    topicId: int
    outlineId: Optional[int]
    outlineEntityId: Optional[int]
    jobId: Optional[int]
    job: Literal['GENERATE_OUTLINE', 'GENERATE_CONTENT', 'RESUME_JOB']
    contentType: Optional[Literal['LESSON', 'LESSON_INTERACTIVES', 'INTERACTIVES']]
    entityType: Optional[Literal['Topic', 'Course', 'Chapter', 'Page',]]
    promptCollection: Optional[str]
    language: Optional[str]
    settings: Optional[dict]  # any


class JobController:
    def __init__(self):
        # Don't let previous jobs interfere with current jobs.
        # Not the best idea but perfect is the enemy of good.
        # We also keep a copy of every event in the database.
        redis.Redis().flushall()

    def dispatch(self, job_event, job_id=None):
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


    def compile_page_interactives(self, topicId: int):
        topic = db.get(Topic, topicId)
        pages = Outline.get_entities_by_type(db, topic.master_outline_id, 'Page')
        page_ids = [page.id for page in pages]

        job_data = {
            'topicId': topic.id,
            'outlineId': topic.master_outline_id,
            'pageIds': page_ids
        }

        job_event = CompileInteractivesToPagesJobRequested(job_data)
        self.dispatch(job_event)


    def get_job_data(self, params):
        job_data = {
            'jobId': params['jobId'],
            'topicId': params['topicId'],
            'outlineId': params['outlineId'],
            'outlineEntityId': params['outlineEntityId'],
        }
        return {k: v for k, v in job_data.items() if v is not None}


    @staticmethod
    def get_all():
        return db.query(JobStore).all()


    @staticmethod
    def run_job(params: JobParams):
        # Determine job type
        job_name = params['job']
        match job_name:
            case 'GENERATE_OUTLINE':
                return JobController.generate_outline(params)
            case 'GENERATE_CONTENT':
                return JobController.generate_page_material(params)
            case 'RESUME_JOB':
                return JobController.resume_job(params)


    @staticmethod
    def generate_outline(params: JobParams):
        controller = JobController()
        job_data = controller.get_job_data(params)
        job_event = GenerateOutlineJobRequested(job_data)
        return controller.dispatch(job_event)


    @staticmethod
    def generate_page_material(params: JobParams):
        controller = JobController()
        print(params)
        job_data = controller.get_job_data(params)

        match params['contentType']:
            case 'LESSON':
                job_event = GeneratePagesFromOutlineJobRequested(job_data)
                controller.dispatch(job_event)
            case 'LESSON_INTERACTIVES':
                job_event = GeneratePagesFromOutlineJobRequested(job_data)
                controller.dispatch(job_event)
                job_event = GeneratePageInteractivesJobRequested(job_data)
                controller.dispatch(job_event)
                controller.compile_page_interactives(job_data['topicId'])
            case 'INTERACTIVES':
                job_event = GeneratePageInteractivesJobRequested(job_data)
                controller.dispatch(job_event)
                controller.compile_page_interactives(job_data['topicId'])


    @staticmethod
    def resume_job(params: JobParams):
        controller = JobController()
        job_data = controller.get_job_data(params)
        job = db.get(JobStore, job_data['jobId'])
        last_event = db.query(EventStore).filter_by(job_id=job.id).order_by(EventStore.id.desc()).first()
        job_event = pydoc.locate(f'src.events.events.{last_event.name}')(last_event.data)
        controller.dispatch(job_event)

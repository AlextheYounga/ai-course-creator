from db.db import DB, Topic, Outline, OutlineEntity, JobStore
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker
from src.events.events import GenerateOutlineJobRequested, GeneratePagesFromOutlineJobRequested

db = DB()


class JobController:
    @staticmethod
    def get_all():
        return db.query(JobStore).all()


    @staticmethod
    def determine_job(payload: dict):
        job_type = payload['jobType']
        match job_type:
            case 'GenerateOutline':
                return JobController.generate_outline(payload)
            case 'GenerateOutlinePages':
                return JobController.generate_pages_from_outline(payload)


    # Generate topic outline
    @staticmethod
    def generate_outline(payload: dict):
        topic = db.get(Topic, payload['topicId'])

        job_data = {
            'topidId': topic.id,
        }

        job_event = GenerateOutlineJobRequested(job_data)
        JobController.dispatch(job_event)
        return 'Success', 201


    @staticmethod
    def generate_pages_from_outline(payload: dict):
        entity_type = payload.get('outlineEntityType', None)

        # If entity type is not a topic, we need to get the outline entity id
        if entity_type != 'Topic':
            entity_id = payload['id']
            outline_entity = db.query(OutlineEntity).filter(
                OutlineEntity.outline_id == outline.id,
                OutlineEntity.entity_id == entity_id,
                OutlineEntity.entity_type == entity_type,
            ).first()
            payload['outlineEntityId'] = outline_entity.id

        topic = db.get(Topic, payload['topic_id'])
        outline = db.get(Outline, topic.master_outline_id)

        job_data = {
            'topidId': topic.id,
            'outlineId': outline.id,
        }

        job_event = GeneratePagesFromOutlineJobRequested(job_data)
        JobController.dispatch(job_event)
        return 'Success', 201


    @staticmethod
    def dispatch(triggering_event):
        queue_context = QueueContext()
        storage_queue = StorageQueue()
        job_queue = JobQueue(storage_queue, 'main_queue')

        job = Job({'data': triggering_event.serialize()})
        job_queue.enqueue(job)

        worker = Worker(queue_context, storage_queue, job_queue)
        worker.perform_async()

        return True

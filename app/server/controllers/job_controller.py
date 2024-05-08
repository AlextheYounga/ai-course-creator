from db.db import DB, Topic, Outline, OutlineEntity, JobStore
from src.jobs import QueueContext, StorageQueue, JobQueue, Job, Worker
from src.events.events import GenerateOutlineRequested, GenerateOutlineMaterialRequested, GeneratePagesFromOutlineEntityRequested

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
            case 'GenerateOutlineMaterial':
                entity_type = payload.get('entityType', None)
                if entity_type == 'Topic':
                    return JobController.generate_outline_material(payload)
                return JobController.generate_outline_entities(payload)


    # Generate topic outline
    @staticmethod
    def generate_outline(payload: dict):
        topic = db.get(Topic, payload['topicId'])

        job_data = {
            'topidId': topic.id,
        }

        job_event = GenerateOutlineRequested(job_data)
        JobController.dispatch(job_event)
        return 'Success', 201


    # Generate full outline material
    @staticmethod
    def generate_outline_material(payload: dict):
        topic = db.get(Topic, payload['topic_id'])
        outline = db.get(Outline, topic.master_outline_id)

        job_data = {
            'topidId': topic.id,
            'outlineId': outline.id,
        }

        job_event = GenerateOutlineMaterialRequested(job_data)
        JobController.dispatch(job_event)
        return 'Success', 201


    # Generate specific sections (outline entities) from outline
    @staticmethod
    def generate_outline_entities(payload: dict):
        entity_id = payload['id']
        entity_type = payload['entityType']
        topic = db.get(Topic, payload['topicId'])
        outline = db.get(Outline, topic.master_outline_id)

        outline_entity = db.query(OutlineEntity).filter(
            OutlineEntity.outline_id == outline.id,
            OutlineEntity.entity_id == entity_id,
            OutlineEntity.entity_type == entity_type,
        ).first()

        job_data = {
            'topidId': topic.id,
            'outlineId': outline.id,
            'outlineEntityId': outline_entity.id
        }

        job_event = GeneratePagesFromOutlineEntityRequested(job_data)
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

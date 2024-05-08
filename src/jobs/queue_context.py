from src.services.redis_client import get_redis_client
from src.jobs.notification_service import NotificationService
from db.db import DB, JobStore
from src.events.base_event import BaseEvent as Event
from src.utils.logger import log_setup


# Cross-cutting concerns go here.
# We want to control instance counts, lifetimes and dependencies explicitly.
# I'd use a DI container for a large project (ie, look at pytest)
# but for a small one, this gives us 80% of what we need with a minor break of SOLID.


class QueueContext:
    def __init__(self, redis_host='127.0.0.1', redis_port=6379):
        redis_client = get_redis_client()
        self.redis = redis_client(host=redis_host, port=redis_port)
        self.notifications = NotificationService(redis_host, redis_port)


    def update_contexts(self, job):
        db = DB()  # Thread local db connection
        event_name = job.data.get('eventName', None)

        job.record = self.save_job(db, job)

        if 'JobFinished' in event_name:
            job.record.set_complete(db)

        return job.record


    def save_job(self, db, job):
        return JobStore.first_or_create(db, job)

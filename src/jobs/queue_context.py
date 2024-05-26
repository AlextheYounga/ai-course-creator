from src.services.redis_client import get_redis_client
from src.jobs.notification_service import NotificationService
from db.db import DB, JobStore


# Cross-cutting concerns go here.
# We want to control instance counts, lifetimes and dependencies explicitly.
# I'd use a DI container for a large project (ie, look at pytest)
# but for a small one, this gives us 80% of what we need with a minor break of SOLID.


class QueueContext:
    def __init__(self, redis_host='127.0.0.1', redis_port=6379):
        redis_client = get_redis_client()
        self.db = DB()  # Thread local db session
        self.redis = redis_client(host=redis_host, port=redis_port)
        self.notifications = NotificationService(redis_host, redis_port)

    def queue_still_running(self, job_queue):
        return job_queue.queue.length(job_queue.pending_queue) > 0

    def save_job(self, job):
        db = DB()  # Thread local db session
        return JobStore.first_or_create(db, job)

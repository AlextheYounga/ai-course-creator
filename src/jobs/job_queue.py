import json
from .job import Job

# JobQueue manages the state of jobs in the system
# It should be able to enqueue, dequeue, complete, fail and error jobs.
# It should NOT know anything about the jobs themselves or the underlying storage(s).


class JobQueue:
    def __init__(self, storage_queue, queue_name, notification_service=None):
        self.queue = storage_queue
        self.queue_name = queue_name
        self.notification_service = notification_service

        self.pending_queue = f"{queue_name}:pending"
        self.completed_queue = f"{queue_name}:completed"
        self.failed_queue = f"{queue_name}:failed"
        self.error_queue = f"{queue_name}:error"

    def notify(self, message, queue):
        if self.notification_service is not None:
            self.notification_service.notify(message, queue)


    def _add(self, job, queue_name):
        serialized_job = json.dumps(job.serialize(), ensure_ascii=False)
        self.queue.put(queue_name, serialized_job)
        # Drop a notification that the job has been added to whichever queue, so that anyone who cares knows what's going on.
        self.notify(serialized_job, f"{queue_name}:notifications")


    def fail(self, job):
        self._add(job, self.failed_queue)

    def complete(self, job):
        self._add(job, self.completed_queue)

    def error(self, job):
        self._add(job, self.error_queue)

    def enqueue(self, job):
        self._add(job, self.pending_queue)

    def dequeue(self):
        serialized_job = self.queue.get(self.pending_queue)
        job_data = json.loads(serialized_job)
        return Job.deserialize(job_data)

import threading


class Worker:
    def __init__(self, queue_context, storage_queue, job_queue):
        self.context = queue_context
        self.storage_queue = storage_queue
        self.job_queue = job_queue
        self.running = True
        self.thread = None

    def perform(self):
        while self.running:
            self.handle()

    def perform_async(self):
        self.thread = threading.Thread(target=self.perform, name="Worker-Thread")
        self.thread.start()

    def handle(self):
        job = self.job_queue.dequeue()
        job.run(self.context)  # Pass in the active context; jobs should know as little about the outside world as possible.

        # If here, the job has finished running
        self._update_queue_statuses(job)
        self._add_next_jobs_to_queue(job)

        # Notify the system of the job's status after processing
        self.context.notifications.notify({'jobId': job.id, 'status': job.status}, "jobs:status_changed")

        # If all job events completed, we can stop the worker
        if not self.context.queue_still_running(self.job_queue):
            job.record.set_complete(self.context.db)
            self.finish()

    def _update_queue_statuses(self, job):
        match job.status:
            case 'completed':
                self.job_queue.complete(job)  # move this job to the completed queue
            case 'failed':
                self.job_queue.fail(job)
            case 'error':
                self.job_queue.error(job)
            case 'in_progress':
                if job.resumable:  # If the job is resumable, we can re-enqueue it, otherwise that's a state error
                    self.job_queue.enqueue(job)
                else:
                    job.error()
            case 'pending':
                raise ValueError("Job should not be in pending state")
            case _:
                raise ValueError(f"Invalid job status: {job.status}")


    def _add_next_jobs_to_queue(self, job):
        match job.status:
            case "completed" | "failed":
                for next_job in job.next_jobs():
                    self.job_queue.enqueue(next_job)


    def finish(self):
        self.running = False

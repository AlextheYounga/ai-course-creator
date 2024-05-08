import threading


class Worker:
    def __init__(self, queue_context, storage_queue, job_queue):
        self.context = queue_context
        self.storage_queue = storage_queue
        self.job_queue = job_queue
        self.running = True
        self.thread = None
        self.stop_event = None

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

        # Update storage contexts with latest job data
        job.record = self.context.update_contexts(job)

        # This is where we add our next jobs to the queue
        match job.status:
            case "completed" | "failed":
                for next_job in job.next_jobs():
                    self.job_queue.enqueue(next_job)

        # Notify the system of the job's status after processing
        self.context.notifications.notify({'jobId': job.id, 'status': job.status}, "jobs:status_changed")

        # If all job events completed, we can stop the worker
        if job.record.status == 'completed':
            self.finish()



    def finish(self):
        self.running = False

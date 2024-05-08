from cuid import cuid
from src.events.events import *

# An individual job in the system.
# Note that creation and execution use the same class.

# There are two ways to use such a job class:
# 1. Subclass it and override the work method.
# 2. Pass in a function to the constructor that does the work.

# 1 is preferred when the serialization or construction is complex, and 2 is preferred when simple.


class Job:
    def __init__(self, deserialized_job={}, resumable=False):
        self.data = deserialized_job.get('data', {})
        self.id = deserialized_job.get('id', cuid())
        self.status = deserialized_job.get('status', 'pending')
        self.resumable = resumable  # If we have implemented a way to resume this job, set to true
        self.context = None
        self.record = None
        self.next = {
            "completed": [],
            "failed": [],
        }

    def complete(self):
        self.status = 'completed'

    def run(self, context):
        self.context = context
        self.status = 'in_progress'
        self.data.update({'jobId': self.id})
        self.work()

    def serialize(self):
        return {
            'data': self.data,
            'status': self.status,
            'id': self.id,
        }

    @classmethod
    def deserialize(cls, deserialized_job):
        job = cls(deserialized_job)
        return job

    def next_jobs(self):
        return self.next[self.status]

    def add_next(self, job, on='completed'):
        self.next[on].append(job)

    def work(self):
        job_event = Event.deserialize_from_job(self)
        next_job_events = Event.trigger(job_event)
        if not next_job_events: return self.complete()

        for next_event in next_job_events:
            self.add_next(Job({
                'id': self.id,
                'data': next_event.serialize()
            }))

        self.complete()

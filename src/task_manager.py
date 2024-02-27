from pytz import utc
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_ADDED
from src.events.event_listener import EventListener


class MyJob:
    def run():
        print("Hello World")


jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

executors = {
    'default': ThreadPoolExecutor(1),
    'processpool': ProcessPoolExecutor(3)
}

job_defaults = {'coalesce': False, 'max_instances': 1}


def create_scheduler():
    listener = EventListener()
    scheduler = BlockingScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
    scheduler.add_listener(listener.listen, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    scheduler.add_job(MyJob.run, 'interval', seconds=5, id="myJob", name="My Job", replace_existing=True)
    scheduler.start()

    return scheduler


SCHEDULER = create_scheduler()

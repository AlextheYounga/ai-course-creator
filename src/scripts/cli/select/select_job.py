import inquirer
from db.db import DB, Topic
from .select_topic import select_topic
from .select_jobstore import select_jobstore
from app.server.controllers.job_controller import JobController


def select_job():
    db = DB()
    topic_name = select_topic()
    topic = Topic.first_or_create(db, name=topic_name)

    base_tasks = [
        'Generate Outline',
        'Generate Page Material With Interactives',
        'Generate Page Material Only',
        'Generate Interactives',
        'Compile Interactives',
        'Resume Job',
    ]

    tasks = [
        inquirer.List('task',
                      message="Select task",
                      choices=list(base_tasks)),
    ]

    choice = inquirer.prompt(tasks, raise_keyboard_interrupt=True)
    task = choice['task']

    match task:
        case 'Generate Outline':
            params = {'topicId': topic.id, 'jobName': 'GENERATE_OUTLINE'}
            return JobController.generate_outline(params)
        case 'Generate Page Material With Interactives':
            params = {'topicId': topic.id, 'jobName': 'GENERATE_COTENT', 'contentType': 'LESSON_INTERACTIVES'}
            return JobController.generate_page_material(params)
        case 'Generate Page Material Only':
            params = {'topicId': topic.id, 'jobName': 'GENERATE_COTENT', 'contentType': 'LESSON'}
            return JobController.generate_page_material(params)
        case 'Generate Interactives':
            params = {'topicId': topic.id, 'jobName': 'GENERATE_COTENT', 'contentType': 'INTERACTIVES'}
            return JobController.generate_page_material(params)
        case 'Resume Job':
            job = select_jobstore()
            params = {'topicId': topic.id, 'jobId': job.id, 'jobName': 'RESUME_JOB'}
            return JobController.resume_job(params)
        case 'Compile Interactives':
            controller = JobController()
            return controller.compile_page_interactives(topic.id)

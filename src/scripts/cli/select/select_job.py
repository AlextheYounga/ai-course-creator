import inquirer
from db.db import DB, Topic
from .select_topic import select_topic
from .select_jobstore import select_jobstore
from app.server.controllers.job_controller import JobController


def select_job():
    db = DB()
    topic_name = select_topic()
    topic = db.query(Topic).filter(Topic.name == topic_name).first()

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
    params = {'topicId': topic.id, "outlineId": topic.master_outline_id}

    match task:
        case 'Generate Outline':
            params.update({'jobName': 'GENERATE_OUTLINE'})
            return JobController.generate_outline(params)
        case 'Generate Page Material With Interactives':
            params.update({'jobName': 'GENERATE_CONTENT', 'contentType': 'LESSON_INTERACTIVES'})
            return JobController.generate_page_material(params)
        case 'Generate Page Material Only':
            params.update({'jobName': 'GENERATE_CONTENT', 'contentType': 'LESSON'})
            return JobController.generate_page_material(params)
        case 'Generate Interactives':
            params.update({'jobName': 'GENERATE_CONTENT', 'contentType': 'INTERACTIVES'})
            return JobController.generate_page_material(params)
        case 'Resume Job':
            job = select_jobstore()
            params.update({'jobId': job.id, 'jobName': 'RESUME_JOB'})
            return JobController.resume_job(params)
        case 'Compile Interactives':
            controller = JobController()
            return controller.compile_page_interactives(topic.id)

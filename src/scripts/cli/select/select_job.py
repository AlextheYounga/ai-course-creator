import inquirer
from db.db import DB, Topic
from .select_topic import select_topic
from ..run_jobs import generate_outline, generate_page_material, generate_page_interactives, compile_page_interactives, resume_job


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
            return generate_outline(topic)
        case 'Generate Page Material With Interactives':
            return generate_page_material(topic)
        case 'Generate Page Material Only':
            return generate_page_material(topic, has_interactives=False)
        case 'Generate Interactives':
            return generate_page_interactives(topic)
        case 'Compile Interactives':
            return compile_page_interactives(topic)
        case 'Resume Job':
            return resume_job()

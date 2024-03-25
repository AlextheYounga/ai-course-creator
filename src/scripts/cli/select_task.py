import inquirer
from db.db import DB, Topic
from .select_topic import select_topic
from .select_generate_content import select_generate_content
from src.commands.generate_outline import GenerateOutline


def _generate_outline(topic: Topic):
    task = GenerateOutline(topic.id)
    task.run()


def select_task():
    topic_name = select_topic()
    topic = Topic.first_or_create(DB, name=topic_name)

    base_tasks = {
        'Generate Outline': _generate_outline,
        'Generate Content': select_generate_content,
        'Continue Thread': continue_thread
    }

    tasks = [
        inquirer.List('task',
                      message="Select task",
                      choices=list(base_commands.keys())),
    ]

    choice = inquirer.prompt(tasks)
    task = choice['task']
    task_function = base_tasks[task]

    # Dynamic function call
    task_function(topic)

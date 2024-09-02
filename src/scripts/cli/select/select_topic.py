import os
import setproctitle
import inquirer
from db.db import DB, Topic
from src.utils.files import read_yaml_file

db = DB()


def _create_new_topic_from_prompt():
    settings_choices = [
        inquirer.List('topicSettings',
                      message="Where should we look for topic settings?",
                      choices=[
                          'Use Default Settings',
                          'Use Topics Config File',
                      ]),
    ]

    topic_name = inquirer.text(message="Enter new topic name")
    topic_record = db.query(Topic).filter(Topic.name == topic_name).first()
    if topic_record: return topic_record

    settings_choice = inquirer.prompt(settings_choices, raise_keyboard_interrupt=True)
    settings_src = settings_choice['topicSettings']

    settings = {}
    match settings_src:
        case 'Use Default Settings':
            settings = Topic.default_settings()
        case 'Use Topics Config File':
            if os.path.exists("configs/topics.yaml"):
                topics_data = read_yaml_file("configs/topics.yaml")
                settings = topics_data['topics'].get(topic_name, None)

    new_topic_record = Topic(
        name=topic_name,
        slug=Topic.make_slug(topic_name),
        properties=settings
    )
    db.add(new_topic_record)
    db.commit()
    return new_topic_record.name


def select_topic():
    topic_records = db.query(Topic.name).all()

    if len(topic_records) == 0:
        return _create_new_topic_from_prompt()

    topic_choices = [record[0] for record in topic_records]
    topic_choices.sort()
    topic_choices = ['Create New', 'All', *topic_choices]

    choices = [
        inquirer.List('topic',
                      message="Which topic would you like to generate course material for?",
                      choices=topic_choices),
    ]

    choice = inquirer.prompt(choices, raise_keyboard_interrupt=True)
    answer = choice['topic']

    if (answer == 'Create New'):
        answer = _create_new_topic_from_prompt()

    setproctitle.setproctitle(f"Course Creator - {answer}")

    return answer

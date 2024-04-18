import setproctitle
import inquirer
from db.db import DB, Topic
from src.utils.files import read_yaml_file


def select_topic():
    topic_records = DB.query(Topic.name).all()
    topic_names_from_db = [record[0] for record in topic_records]

    topics_file = "storage/topics.yaml"
    topics = read_yaml_file(topics_file)
    topic_names_from_file = list(topics['topics'].keys())

    topic_choices = list(set(topic_names_from_db + topic_names_from_file))

    choices = [
        inquirer.List('topic',
                      message="Which topic would you like to generate course material for?",
                      choices=topic_choices),
    ]

    choice = inquirer.prompt(choices)
    answer = choice['topic']

    setproctitle.setproctitle(answer)

    return answer

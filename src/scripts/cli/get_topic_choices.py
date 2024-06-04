import setproctitle
from db.db import DB, Topic
from src.utils.files import read_yaml_file


def get_topics():
    db = DB()
    topic_records = db.query(Topic.name).all()
    topic_names_from_db = [record[0] for record in topic_records]

    topics_file = "configs/topics.yaml"
    topics = read_yaml_file(topics_file)
    topic_names_from_file = list(topics['topics'].keys())

    topic_choices = list(set(topic_names_from_db + topic_names_from_file))

    setproctitle.setproctitle(topic_choices[0])

    return topic_choices

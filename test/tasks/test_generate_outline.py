from ..mocks.db import *
from src.tasks.generate_outline import GenerateOutline
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler


TOPIC = 'Ruby on Rails'


def __setup_test():
    truncate_tables()
    topics_file = "storage/topics.example.yaml"
    ScanTopicsFileHandler(topics_file=topics_file).handle()


def test_generate_outline():
    __setup_test()

    topic = DB.query(Topic).filter(Topic.name == TOPIC).first()
    task = GenerateOutline(topic.id)
    outline = task.run()

    assert outline.id is not None

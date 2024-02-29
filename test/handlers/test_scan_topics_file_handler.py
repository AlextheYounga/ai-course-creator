from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
from ..mocks.db import *


def __setup_test():
    truncate_tables()


def test_scan_topics_file_handler():
    __setup_test()

    handler = ScanTopicsFileHandler(topics_file="storage/topics.example.yaml")
    topics = handler.handle()

    assert len(topics) == 3

    for topic in topics:
        assert topic.id is not None
        assert topic.name is not None
        assert topic.slug is not None
        assert topic.properties['prompts'] is not None
        assert topic.properties['language'] is not None

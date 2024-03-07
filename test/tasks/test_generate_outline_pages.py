from ..mocks.db import *
from src.tasks.generate_outline_pages import GenerateOutlinePages
from src.handlers.create_new_thread_handler import CreateNewThreadHandler
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
from src.handlers.outlines.create_new_outline_handler import CreateNewOutlineHandler


TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()
LOG_FILE = 'test/data/test.log'


def __setup_test():
    truncate_tables()
    thread = CreateNewThreadHandler({'eventName': __name__}).handle()
    topics_file = "storage/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()
    CreateNewOutlineHandler({'threadId': thread.id, 'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()


def test_generate_outline_pages():
    __setup_test()

    failed_events = [
        'ExistingPageSoftDeletedForPageRegeneration',
    ]

    task = GenerateOutlinePages(topic_id=1)

    task.run()

    pages = DB.query(Page).all()
    assert len(pages) == 77

    for page in pages:
        assert page.content is not None
        assert page.content != ''
        assert page.generated
        assert page.topic_id == 1
        assert page.type in ['lesson', 'challenge', 'final-skill-challenge']
        assert page.chapter_id is not None
        assert page.hash is not None

    logs = open(LOG_FILE, 'r').read()

    for event in failed_events:
        assert event not in logs

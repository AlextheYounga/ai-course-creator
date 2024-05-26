from ..mocks.mock_db import *
from src.handlers.get_next_page_to_generate_from_job_handler import GetNextPageToGenerateFromJobHandler
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
from src.handlers.create_new_outline_handler import CreateNewOutlineHandler

TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()


def __setup_test():
    truncate_tables()
    topics_file = "configs/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()
    CreateNewOutlineHandler({'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()


def test_get_next_page_to_generate_from_thread_using_only_outline_id():
    __setup_test()

    triggered_event = GetNextPageToGenerateFromJobHandler({
        'jobId': 1,
        'outlineId': 1,
        'topicId': 1
    }).handle()

    assert triggered_event is not None
    assert triggered_event.data.get('pageId', None) is not None
    assert triggered_event.data['pageId'] == 1
    assert triggered_event.data.get('totalSteps', None) == 54
    assert triggered_event.__class__.__name__ == 'GenerateLessonPageProcessStarted'


def test_get_next_page_to_generate_from_thread_using_chapter_outline_entity_id():
    __setup_test()

    triggered_event = GetNextPageToGenerateFromJobHandler({
        'jobId': 1,
        'outlineId': 1,
        'outlineEntityId': 6,
        'topicId': 1
    }).handle()

    assert triggered_event is not None
    assert triggered_event.data.get('pageId', None) is not None
    assert triggered_event.data.get('totalSteps', None) == 4
    assert triggered_event.__class__.__name__ == 'GenerateLessonPageProcessStarted'

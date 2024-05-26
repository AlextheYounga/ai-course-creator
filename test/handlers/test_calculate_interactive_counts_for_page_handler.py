from ..mocks.mock_db import *
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
from src.handlers.create_new_outline_handler import CreateNewOutlineHandler
from src.handlers.calculate_interactive_counts_for_page_handler import CalculateInteractiveCountsForPageHandler

TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()


def __setup_test():
    truncate_tables()
    topics_file = "configs/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()
    CreateNewOutlineHandler({'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()


def test_calculate_interactive_counts_for_page_handler():
    __setup_test()

    event = CalculateInteractiveCountsForPageHandler({
        'outlineId': 1,
        'pageId': 1,
        'topicId': 1,
    }).handle()

    print(event)

    # for event in next_events:
    #     assert event.__class__.__name__ in [
    #         'GenerateMultipleChoicePageInteractivesProcessStarted',
    #         'GenerateCodeEditorPageInteractiveProcessStarted',
    #         'GenerateCodepenPageInteractiveProcessStarted'
    #     ]
    #     print(event.__class__.__name__)
    #     print(event.data['interactives'])

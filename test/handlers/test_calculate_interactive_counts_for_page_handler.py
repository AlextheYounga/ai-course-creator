from ..mocks.mock_db import *
from src.handlers.create_new_outline_handler import CreateNewOutlineHandler
from src.handlers.calculate_interactive_counts_for_page_handler import CalculateInteractiveCountsForPageHandler

TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()


def __setup_test():
    truncate_tables()
    import_sql_from_file(DB_PATH, 'test/fixtures/sql/topic.sql')
    CreateNewOutlineHandler({'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()


def test_calculate_interactive_counts_for_page_handler():
    __setup_test()

    event = CalculateInteractiveCountsForPageHandler({
        'outlineId': 1,
        'pageId': 1,
        'topicId': 1,
    }).handle()

    assert event.data is not None
    assert event.data['interactives'] is not None

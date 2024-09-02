from ..mocks.mock_db import *
from src.handlers.create_lesson_page_prompt_handler import CreateLessonPagePromptHandler
from src.handlers.create_new_outline_handler import CreateNewOutlineHandler

TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()



def __setup_test():
    truncate_tables()
    import_sql_from_file(DB_PATH, 'test/fixtures/sql/topic.sql')
    CreateNewOutlineHandler({'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()


def test_create_lesson_page_prompt_handler():
    db = DB()
    __setup_test()

    CreateLessonPagePromptHandler({
        'threadId': 1,
        'outlineId': 1,
        'pageId': 1,
        'topicId': 1,
    }).handle()

    prompt = db.query(Prompt).first()

    assert prompt is not None
    assert prompt.content is not None

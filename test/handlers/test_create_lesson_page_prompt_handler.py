from ..mocks.db import *
from src.handlers.pages.create_lesson_page_prompt_handler import CreateLessonPagePromptHandler
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
from src.handlers.outlines.create_new_outline_handler import CreateNewOutlineHandler
from sqlalchemy import Integer

TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()
LOG_FILE = 'test/data/test.log'
DB_PATH = 'test/data/test.db'


def __setup_test():
    truncate_tables()
    thread = Thread.start(DB, __name__)
    topics_file = "storage/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()
    CreateNewOutlineHandler({'threadId': thread.id, 'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()


def test_create_lesson_page_prompt_handler():
    __setup_test()

    CreateLessonPagePromptHandler({
        'threadId': 1,
        'outlineId': 1,
        'pageId': 1,
        'topicId': 1,
    }).handle()

    prompt = DB.query(Prompt).first()

    assert prompt is not None
    assert prompt.content is not None
    assert '[multipleChoice' in prompt.content
    assert '[fillBlank' in prompt.content
    assert '[codeEditor' in prompt.content
    assert '[trueFalse' in prompt.content
    assert '[codepen' not in prompt.content

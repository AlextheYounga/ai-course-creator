from ..mocks.mock_db import *
from src.handlers.create_code_editor_interactives_prompt_handler import CreateCodeEditorInteractivesPromptHandler
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
from src.handlers.create_new_outline_handler import CreateNewOutlineHandler

TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()
PAGE_MATERIAL = open('test/fixtures/responses/page.md').read()
INTERACTIVES_RECORDS = open('test/fixtures/sql/interactives.sql').read()


def __setup_test():
    truncate_tables()
    db = DB()

    topics_file = "configs/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()
    CreateNewOutlineHandler({'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()

    # Update page record
    page = db.get(Page, 1)
    content_hash = Page.hash_page(PAGE_MATERIAL)
    page.content = PAGE_MATERIAL
    page.hash = content_hash
    page.generated = True

    db.execute(text(INTERACTIVES_RECORDS))
    db.commit()


def test_create_code_editor_interactives_prompt_handler():
    db = DB()
    __setup_test()

    CreateCodeEditorInteractivesPromptHandler({
        'threadId': 1,
        'outlineId': 1,
        'pageId': 1,
        'topicId': 1,
    }).handle()

    prompt = db.query(Prompt).first()

    assert prompt is not None
    assert prompt.content is not None

    question_lines = prompt.content.split("questions:\n```markdown")[1].strip().split('\n')
    assert len(question_lines) == 8

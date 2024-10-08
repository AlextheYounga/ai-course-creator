from ..mocks.mock_db import *
from sqlalchemy.sql import text
from src.handlers.create_new_outline_handler import CreateNewOutlineHandler
from src.handlers.process_multiple_choice_interactives_response_handler import ProcessMultipleChoiceInteractivesResponseHandler

TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()
PAGE_MATERIAL = open('test/fixtures/responses/page.md').read()
PROMPT_RECORD = open('test/fixtures/sql/prompt-code-editor.sql').read()
RESPONSE_RECORD = open('test/fixtures/sql/response-multiple-choice.sql').read()


def __setup_test():
    truncate_tables()
    db = get_session()
    import_sql_from_file(DB_PATH, 'test/fixtures/sql/topic.sql')
    CreateNewOutlineHandler({'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()

    # Update page record
    page = db.get(Page, 1)
    content_hash = Page.hash_page(PAGE_MATERIAL)
    page.content = PAGE_MATERIAL
    page.hash = content_hash
    page.generated = True

    # Create prompt record
    db.execute(text(PROMPT_RECORD))

    # Create response record
    db.execute(text(RESPONSE_RECORD))

    db.commit()


def test_process_multiple_choice_interactive_response_handler():
    __setup_test()

    db = get_session()

    event = ProcessMultipleChoiceInteractivesResponseHandler({
        'topicId': 1,
        'pageId': 1,
        'outlineId': 1,
        'responseId': 1,
        'promptId': 1
    }).handle()

    assert event.__class__.__name__ == 'MultipleChoiceInteractivesSavedFromResponse'

    interactive = db.get(Interactive, 1)

    assert interactive.data is not None
    assert interactive.data['content'] is not None
    assert interactive.data['question'] is not None
    assert interactive.data['answer'] is not None
    assert interactive.data['description'] is not None
    assert interactive.data['difficulty'] is not None

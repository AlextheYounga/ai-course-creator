from ..mocks.db import *
from src.commands.generate_pages_from_outline import GeneratePagesFromOutline
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


def __setup_with_existing():
    truncate_tables()
    import_sql_data_from_file(DB_PATH, 'test/data/test.sql.zip', zipped=True)

    fsc_pages = DB.query(Page).filter(Page.type == 'final-skill-challenge').all()
    for page in fsc_pages:
        page.generated = False
        page.content = None
        page.hash = None
    DB.commit()


def test_generate_pages_from_outline():
    __setup_test()

    bad_events = [
        'ExistingPageSoftDeletedForPageRegeneration',
        'InvalidLessonPageResponseFromOpenAI'
    ]

    task = GeneratePagesFromOutline(topic_id=1, progress_bar=False)

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

    events = DB.query(Event).filter(
        Event.name.in_(bad_events),
        Event.data['threadId'].cast(Integer) == task.thread.id
    ).count()

    assert events == 0


def test_generate_only_outline_fsc_pages():
    __setup_with_existing()

    task = GeneratePagesFromOutline(topic_id=1, page_type='final-skill-challenge', progress_bar=False)

    task.run()

    events = DB.query(Event).filter(
        Event.name == 'ChallengePageResponseProcessedSuccessfully',
        Event.data['threadId'].cast(Integer) == task.thread.id
    ).all()

    assert len(events) == 7
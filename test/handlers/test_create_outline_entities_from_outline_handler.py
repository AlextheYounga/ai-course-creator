from ..mocks.mock_db import *
from src.handlers.create_outline_entities_from_outline_handler import CreateOutlineEntitiesFromOutlineHandler
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
from src.utils.files import read_yaml_file



OUTLINE_DATA = read_yaml_file('test/fixtures/master-outline.yaml')
LOG_FILE = 'test/data/test.log'


def __setup_test():
    truncate_tables()
    db = DB()
    topics_file = "configs/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()

    outline_hash = Outline.hash_outline(OUTLINE_DATA)
    outline = Outline(
        topic_id=1,
        name='series-1',
        outline_data=OUTLINE_DATA,
        hash=outline_hash,
        properties={}
    )

    db.add(outline)
    db.commit()
    db.close()


def test_create_outline_entities_from_outline():
    __setup_test()
    db = DB()
    outline = db.query(Outline).first()
    topic = db.query(Topic).first()

    # Create outline entities
    CreateOutlineEntitiesFromOutlineHandler({
        'outlineId': outline.id,
        'topicId': topic.id
    }).handle()

    outline_entities = db.query(OutlineEntity).all()

    assert len(outline_entities) == 107


def test_duplicate_create_outline_entities_from_outline():
    db = DB()
    outline = db.query(Outline).first()
    topic = db.query(Topic).first()

    # Create outline entities
    CreateOutlineEntitiesFromOutlineHandler({
        'outlineId': outline.id,
        'topicId': topic.id
    }).handle()

    outline_entities = db.query(OutlineEntity).all()

    assert len(outline_entities) == 107

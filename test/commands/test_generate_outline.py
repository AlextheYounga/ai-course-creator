from ..mocks.db import *
from src.commands.generate_outline import GenerateOutline
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
from src.utils.files import read_yaml_file


TOPIC = 'Ruby on Rails'
OUTLINE_DATA = read_yaml_file('test/fixtures/master-outline.yaml')
LOG_FILE = 'test/data/test.log'


def __setup_test():
    truncate_tables()
    topics_file = "storage/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()


def test_generate_outline():
    __setup_test()

    failed_events = [
        'InvalidGenerateSkillsResponseFromOpenAI',
        'InvalidOutlineChunkResponseFromOpenAI',
        'FailedToParseYamlFromOutlineChunkResponse'
    ]

    topic = DB.query(Topic).filter(Topic.name == TOPIC).first()
    task = GenerateOutline(topic.id)
    task.run()

    outline = DB.get(Outline, 1)
    outline_entities_count = DB.query(OutlineEntity).filter(OutlineEntity.outline_id == outline.id).count()

    DB.refresh(topic)

    assert outline.id is not None
    assert outline.topic_id == topic.id
    assert outline.file_path is not None
    assert outline.hash == Outline.hash_outline(OUTLINE_DATA)
    assert topic.master_outline_id == outline.id
    assert outline_entities_count == 107

    logs = open(LOG_FILE, 'r').read()

    for event in failed_events:
        assert event not in logs

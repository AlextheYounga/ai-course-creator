from ..mocks.db import *
from src.handlers.pages.create_final_skill_challenge_prompt_handler import CreateFinalSkillChallengePromptHandler
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
from src.handlers.outlines.create_new_outline_handler import CreateNewOutlineHandler

TOPIC = 'Ruby on Rails'
OUTLINE_DATA = open('test/fixtures/master-outline.yaml').read()


def __setup_test():
    truncate_tables()
    thread = Thread.start(DB, __name__)
    topics_file = "configs/topics.example.yaml"
    ScanTopicsFileHandler({"topicsFile": topics_file}).handle()
    CreateNewOutlineHandler({'threadId': thread.id, 'topicId': 1, 'outlineData': OUTLINE_DATA}).handle()


def test_create_final_skill_challenge_prompt_handler():
    __setup_test()

    CreateFinalSkillChallengePromptHandler({
        'threadId': 1,
        'outlineId': 1,
        'pageId': 1
    }).handle()

    prompt = DB.query(Prompt).first()

    assert prompt is not None
    assert prompt.content is not None
    assert '[multipleChoice' in prompt.content
    assert '[fillBlank' in prompt.content
    assert '[codeEditor' in prompt.content
    assert '[trueFalse' in prompt.content
    assert '[codepen' not in prompt.content

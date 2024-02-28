from ..mocks.openai_mock_service import OpenAIMockService
from ..mocks.db import *
from src.tasks.generate_topic_courses import GenerateTopicCourses


TOPIC = 'Ruby on Rails'


def __setup_test():
    truncate_tables()


def test_generate_topic_courses():
    __setup_test()
    task = GenerateTopicCourses()

from ..utils.helpers import scan_topics_file
from db.db import DB, Topic, Outline
from openai import OpenAI
from .generate_course import GenerateCourse


class GenerateTopicCourses:
    def __init__(self, topic_id: int, llm: OpenAI):
        self.topic = DB.get(Topic, topic_id)
        self.llm_handler = llm
        self.outline = Outline.get_master_outline(DB, self.topic)


    def run(self):
        scan_topics_file()

        courses = Outline.get_entities_by_type(DB, self.outline.id, 'Course')

        for course in courses:
            task = GenerateCourse(self.topic.id, self.llm_handler, course)
            task.run()

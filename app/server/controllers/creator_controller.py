from db.db import DB, Topic, Course, Chapter, Page
from src.creator.course_creator import CourseCreator
from src.llm.openai_handler import OpenAiHandler


class CreatorController:
    @staticmethod
    def generate_entities(payload: dict):
        entity_type = payload['entity_type']
        topic_id = payload.get('topic_id', payload.get('id'))
        topic = DB.get(Topic, topic_id)

        if topic and entity_type:
            creator = CourseCreator(OpenAiHandler, topic.name)

            if entity_type == 'Topic':
                creator.generate_topic_courses()
            elif entity_type == 'Course':
                course = DB.get(Course, payload['id'])
                creator.generate_course(course)
            elif entity_type == 'Chapter':
                chapter = DB.get(Chapter, payload['id'])
                creator.generate_chapter(chapter)
            elif entity_type == 'Page':
                page = DB.get(Page, payload['id'])
                creator.generate_page_material(page)

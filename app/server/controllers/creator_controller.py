from db.db import DB, Topic, Course, Chapter, Page
from src.creator.course_creator import CourseCreator
from src.llm.openai_handler import OpenAiHandler


class CreatorController:
    @staticmethod
    def generate_entities(payload: dict):
        entity_type = payload.data.type
        topic_id = payload.data.get('topic_id', payload.data.get('id'))
        topic = DB.get(Topic, topic_id)

        if topic and entity_type:
            creator = CourseCreator(OpenAiHandler, topic.name)

            if entity_type == 'topic':
                return creator.generate_topic_courses()
            elif entity_type == 'course':
                course = DB.get(Course, payload.data.id)
                return creator.generate_course(course)
            elif entity_type == 'chapter':
                chapter = DB.get(Chapter, payload.data.id)
                return creator.generate_chapter(chapter)
            elif entity_type == 'page':
                page = DB.get(Page, payload.data.id)
                return creator.generate_page_material(page)

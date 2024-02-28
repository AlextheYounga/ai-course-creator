from db.db import DB, Topic, Course, Chapter, Page
from src.creator.course_creator import CourseCreator
from services.openai_service import OpenAiService


class CreatorController:
    @staticmethod
    def generate_entities(payload: dict):
        entityType = payload['entityType']
        topic_id = payload.get('topic_id', payload.get('id'))
        topic = DB.get(Topic, topic_id)

        if topic and entityType:
            creator = CourseCreator(OpenAiService, topic.name)

            if entityType == 'Topic':
                creator.generate_topic_courses()
            elif entityType == 'Course':
                course = DB.get(Course, payload['id'])
                creator.generate_course(course)
            elif entityType == 'Chapter':
                chapter = DB.get(Chapter, payload['id'])
                creator.generate_chapter(chapter)
            elif entityType == 'Page':
                page = DB.get(Page, payload['id'])
                creator.generate_page_material(page)

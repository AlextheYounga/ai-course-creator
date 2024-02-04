from .select_content_item import select_content_item_from_hierachy
from src.llm.openai_handler import OpenAiHandler
from src.creator.course_creator import CourseCreator
from db.db import Topic


def generate_outline(topic: Topic):
    creator = CourseCreator(OpenAiHandler, topic.name)
    return creator.create_outline()


def generate_topic_courses(data: dict):
    topic = data.get('topic')
    creator = CourseCreator(OpenAiHandler, topic.name)
    return creator.generate_topic_courses()


def generate_topic_fsc(data: dict):
    topic = data.get('topic')
    creator = CourseCreator(OpenAiHandler, topic.name)
    return creator.create_topic_final_skill_challenges()


def generate_course(data: dict):
    topic = data.get('topic')
    course = select_content_item_from_hierachy(topic, 'Course')
    creator = CourseCreator(OpenAiHandler, topic.name)
    return creator.generate_course_material(course)


def generate_course_fsc(data: dict):
    topic = data.get('topic')
    course = select_content_item_from_hierachy(topic, 'Course')
    creator = CourseCreator(OpenAiHandler, topic.name)
    return creator.generate_course_final_skill_challenge(course)


def generate_chapter(data: dict):
    topic = data.get('topic')
    creator = CourseCreator(OpenAiHandler, topic.name)
    chapter = select_content_item_from_hierachy(topic, 'Chapter')
    return creator.generate_chapter_material(chapter)


def generate_page(data: dict):
    topic = data.get('topic')
    page = select_content_item_from_hierachy(topic, 'Page')
    creator = CourseCreator(OpenAiHandler, topic.name)
    return creator.dynamic_generate_page_material(page.type, page)


def dynamic_generate_material(data: dict):
    topic = data.get('topic')
    content_type = data.get('contentType')
    hierarchy = data.get('hierarchy')
    creator = CourseCreator(OpenAiHandler, topic.name)
    record = select_content_item_from_hierachy(topic, hierarchy)
    return creator.dynamic_generate_page_material(content_type, record)

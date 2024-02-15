from .select_hierarchy import select_hierarchy
from .select_content_function import select_content_function
from .select_content_item import select_content_item_from_hierachy
from src.llm.openai_handler import OpenAiHandler
from src.creator.course_creator import CourseCreator
from db.db import DB, Topic, Outline


def select_generate_content(topic: Topic):
    creator = CourseCreator(OpenAiHandler, topic.name)

    content_function_mapping = {
        'Topic': {
            'All': creator.generate_topic_courses,
            'Page Material': creator.create_topic_page_material,
            'Practice Skill Challenges': creator.create_topic_practice_skill_challenges,
            'Final Skill Challenges': creator.create_topic_final_skill_challenges,
        },
        'Course': {
            'All': creator.generate_course,
            'Page Material': creator.generate_entity_page_material,
            'Practice Skill Challenges': creator.generate_course_challenges,
            'Final Skill Challenges': creator.generate_course_final_skill_challenge,
        },
        'Chapter': {
            'All': creator.generate_chapter,
            'Page Material': creator.generate_entity_page_material,
            'Practice Skill Challenges': creator.generate_chapter_challenge,
        },
        'Page': creator.generate_page_material,
    }

    # Prompt user for hierarchy
    hierarchy = select_hierarchy()

    if hierarchy == 'Page':
        subroutine_function = content_function_mapping[hierarchy]
    else:
        # Select sub function for hierarchy
        content_type = select_content_function(hierarchy)
        subroutine_function = content_function_mapping[hierarchy][content_type]

    if hierarchy == 'Topic':
        return subroutine_function()

    # Select db record to run sub function on
    record = select_content_item_from_hierachy(topic, hierarchy)
    return subroutine_function(record)

from .select_hierarchy import select_hierarchy
from .select_content_function import select_content_function
from .generate_functions import *
from db.db import Topic


def select_generate_content(topic: Topic):
    content_function_mapping = {
        'Topic': {
            'All': generate_topic_courses,
            'Page Material': dynamic_generate_material,
            'Practice Skill Challenges': dynamic_generate_material,
            'Final Skill Challenges': generate_topic_fsc,
        },
        'Course': {
            'All': generate_course,
            'Page Material': dynamic_generate_material,
            'Practice Skill Challenges': dynamic_generate_material,
            'Final Skill Challenges': generate_course_fsc,
        },
        'Chapter': {
            'All': generate_chapter,
            'Page Material': dynamic_generate_material,
            'Practice Skill Challenges': dynamic_generate_material,
        },
        'Page': generate_page,
    }

    content_type_mapping = {
        'All': None,
        'Page Material': 'page',
        'Practice Skill Challenges': 'challenge',
        'Final Skill Challenges': 'final-skill-challenge',
    }

    hierarchy = select_hierarchy()
    content_type = select_content_function(hierarchy)
    subroutine_function = content_function_mapping[hierarchy][content_type]

    data = {
        'topic': topic,
        'hierarchy': hierarchy,
        'contentType': content_type_mapping[content_type],
    }

    return subroutine_function(data)

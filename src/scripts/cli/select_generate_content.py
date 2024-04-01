from .select_hierarchy import select_hierarchy
from .select_hierarchy_content_type import select_hierarchy_content_type
from .select_outline_entity_record import select_outline_entity_record
from src.commands.generate_pages_from_outline_entity import GeneratePagesFromOutlineEntity
from commands.generate_pages_from_outline import GeneratePagesFromOutline
from db.db import Topic


def select_generate_content(topic: Topic):
    type_mapping = {
        'All': None,
        'Page Material': 'lesson',
        'Practice Skill Challenges': 'challenge',
        'Final Skill Challenges': 'final-skill-challenge'
    }

    # Prompt user for hierarchy
    hierarchy = select_hierarchy()

    # Prompt user for content type: (All, Page Material, Practice Skill Challenges, Final Skill Challenges)
    content_type = select_hierarchy_content_type(hierarchy)

    if hierarchy == 'Topic':
        task = GeneratePagesFromOutline(topic.id, type_mapping[content_type])
        return task.run()
    else:
        # Prompt user to select outline entity record from DB; types = Course, Chapter, Page
        record = select_outline_entity_record(topic, hierarchy)
        task = GeneratePagesFromOutlineEntity(topic.id, record.id, type_mapping[content_type])
        return task.run()

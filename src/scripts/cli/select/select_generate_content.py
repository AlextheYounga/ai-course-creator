from .select_hierarchy import select_hierarchy
from .select_outline_entity_record import select_outline_entity_record
from db.db import Topic


def select_generate_content(topic: Topic):
    # Prompt user for hierarchy
    hierarchy = select_hierarchy()

    data = {
        'topicId': topic.id,
        'outlineId': topic.master_outline_id,
    }

    if hierarchy == 'Topic':
        return data

    # Prompt user to select outline entity record from DB; types = Course, Chapter, Page
    record = select_outline_entity_record(topic, hierarchy)
    data['outlineEntityId'] = record.id
    return data

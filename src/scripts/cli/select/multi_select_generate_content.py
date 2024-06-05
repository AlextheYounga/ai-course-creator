from .select_hierarchy import select_hierarchy
from .multi_select_outline_entity_records import multi_select_outline_entity_records
from db.db import Topic


def multi_select_generate_content(topic: Topic):
    # Prompt user for hierarchy
    hierarchy = select_hierarchy()

    data = {
        'topicId': topic.id,
        'outlineId': topic.master_outline_id,
    }

    if hierarchy == 'Topic':
        return [data]

    # Prompt user to select outline entity record from DB; types = Course, Chapter, Page
    records = multi_select_outline_entity_records(topic, hierarchy)

    job_data = []
    for record in records:
        job_data.append({
            **data,
            'outlineEntityId': record.id
        })

    return job_data

import inquirer
from db.db import DB, Topic, Outline, OutlineEntity, Page


def _get_outline_entity_from_item(outline: Outline, entity_type: str, entity_id: int):
    return DB.query(OutlineEntity).filter(
        OutlineEntity.outline_id == outline.id,
        OutlineEntity.entity_id == entity_id,
        OutlineEntity.entity_type == entity_type
    ).first()


def _select_record(items: list, item_type: str):
    item_choices = [item.name for item in items]
    content_select = [
        inquirer.List('contentSelect',
                      message=f"Select {item_type} item",
                      choices=item_choices),
    ]

    user_prompt = inquirer.prompt(content_select)

    if user_prompt != None:
        answer = user_prompt['contentSelect']

        for item in items:
            if item.name == answer:
                return item


def select_outline_entity_record(topic: Topic, hierarchy: str):
    outline = Outline.get_master_outline(DB, topic)
    entities = Outline.get_entities(DB, outline.id)

    if hierarchy not in ['Course', 'Chapter', 'Page']:
        raise ValueError('Invalid hierarchy level.')

    if hierarchy == 'Course':
        entity_record = _select_record(entities['courses'], 'course')
        return _get_outline_entity_from_item(outline, hierarchy, entity_record.id)

    if hierarchy == 'Chapter':
        chapter_items = [chapter for chapter in entities['chapters'] if chapter.name != 'Final Skill Challenge']
        entity_record = _select_record(chapter_items, 'chapter')
        return _get_outline_entity_from_item(outline, hierarchy, entity_record.id)

    if hierarchy == 'Page':
        entity_record = _select_record(entities['pages'], 'page')
        return _get_outline_entity_from_item(outline, hierarchy, entity_record.id)

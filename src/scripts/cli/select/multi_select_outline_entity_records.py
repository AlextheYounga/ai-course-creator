import inquirer
from db.db import DB, Topic, Outline, OutlineEntity, Page

db = DB()


def _get_outline_entities_from_items(outline: Outline, entity_type: str, entity_records):
    entity_record_ids = [entity_record.id for entity_record in entity_records]
    return db.query(OutlineEntity).filter(
        OutlineEntity.outline_id == outline.id,
        OutlineEntity.entity_type == entity_type,
        OutlineEntity.entity_id.in_(entity_record_ids)
    ).all()


def _select_records(items: list, item_type: str):
    item_choices = [item.name for item in items]
    content_select = [
        inquirer.Checkbox('contentSelect',
                          message=f"Select all {item_type} items",
                          choices=item_choices),
    ]

    user_prompt = inquirer.prompt(content_select, raise_keyboard_interrupt=True)
    if user_prompt != None:
        answers = user_prompt['contentSelect']
        selected_items = []
        for answer in answers:
            item_lookup = [item for item in items if item.name == answer][0]
            selected_items.append(item_lookup)

        return selected_items


def multi_select_outline_entity_records(topic: Topic, hierarchy: str):
    outline = Outline.get_master_outline(db, topic)
    entities = Outline.get_entities(db, outline.id)

    if hierarchy not in ['Course', 'Chapter', 'Page']:
        raise ValueError('Invalid hierarchy level.')

    match hierarchy:
        case 'Course':
            entity_records = _select_records(entities['courses'], 'course')
            return _get_outline_entities_from_items(outline, hierarchy, entity_records)

        case 'Chapter':
            chapter_items = [chapter for chapter in entities['chapters'] if chapter.name != 'Final Skill Challenge']
            entity_records = _select_records(chapter_items, 'chapter')
            return _get_outline_entities_from_items(outline, hierarchy, entity_records)

        case 'Page':
            entity_records = _select_records(entities['pages'], 'page')
            return _get_outline_entities_from_items(outline, hierarchy, entity_records)

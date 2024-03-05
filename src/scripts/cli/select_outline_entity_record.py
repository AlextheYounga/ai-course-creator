import inquirer
from db.db import DB, Topic, Outline, OutlineEntity, Page


def _get_outline_entity_from_page(outline: Outline, page: Page):
    return DB.query(OutlineEntity).filter(
        OutlineEntity.outline_id == outline.id,
        OutlineEntity.entity_id == page.id,
        OutlineEntity.entity_type == 'Page'
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

    page_record = None

    if hierarchy == 'Course':
        page_record = _select_record(entities['courses'], 'course')

    if hierarchy == 'Chapter':
        chapter_items = [chapter for chapter in entities['chapters'] if chapter.name != 'Final Skill Challenge']
        page_record = _select_record(chapter_items, 'chapter')

    if hierarchy == 'Page':
        page_record = _select_record(entities['pages'], 'page')

    return _get_outline_entity_from_page(outline, page_record)

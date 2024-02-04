import inquirer
from db.db import DB, Topic, Outline


def select_content_item(items: list, item_type: str):
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


def select_content_item_from_hierachy(topic: Topic, hierarchy: str):
    outline = topic.get_latest_outline()
    entities = Outline.get_entities(DB, outline.id)

    # The default is the topic level, so no need to select pages for topic.
    # Each creator class already knows how to look for pages at the topic level.

    if hierarchy == 'Topic':
        return topic

    if hierarchy == 'Course':
        return select_content_item(entities['courses'], 'course')

    if hierarchy == 'Chapter':
        chapter_items = [chapter for chapter in entities['chapters'] if chapter.name != 'Final Skill Challenge']
        return select_content_item(chapter_items, 'chapter')

    if hierarchy == 'Page':
        return select_content_item(entities['pages'], 'page')

    raise ValueError('Invalid hierarchy level.')

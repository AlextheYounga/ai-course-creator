from db.db import DB, Topic, Course, Chapter, Page
from src.creator.regenerator import Regenerator
from .select_content_item import select_content_item_from_hierachy
import inquirer


def select_regenerate_content(topic: Topic):
    content_level = [
        inquirer.List('contentLevel',
                      message="At which hierarchy would you like to regenerate content?",
                      choices=[
                          'Regenerate Course',
                          'Regenerate Chapter',
                          'Regenerate Page',
                      ]),
    ]

    user_prompt = inquirer.prompt(content_level)

    if user_prompt != None:
        regenerator = Regenerator(topic)
        answer = user_prompt['contentLevel']

        if answer == 'Regenerate Entire Course':
            course = select_content_item_from_hierachy(topic, 'Course')
            return regenerator.regenerate_course(course)

        elif answer == 'Regenerate Chapter':
            chapter = select_content_item_from_hierachy(topic, 'Chapter')
            return regenerator.regenerate_chapter(chapter)

        elif answer == 'Regenerate Specific Page':
            page = select_content_item_from_hierachy(topic, 'Page')
            return regenerator.regenerate_page(page)

        else:
            "You did not select any content. Exiting..."

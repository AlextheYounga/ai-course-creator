from db.db import DB, Topic, Course, Chapter, Page
from src.creator.pages.page_processor import PageProcessor
import inquirer


def _get_item_by_name(name, items):
    for item in items:
        if item.name == name:
            return item

    raise Exception("You did not select an item. Exiting...")


def _select_content_item(items):
    content_select = [
        inquirer.List('contentSelect',
                      message="Select content item",
                      choices=items),
    ]

    user_prompt = inquirer.prompt(content_select)

    if user_prompt != None:
        answer = user_prompt['contentSelect']
        return answer


def select_regenerate_content(topic):
    topic_record = DB.query(Topic).filter(Topic.name == topic).first()

    content_level = [
        inquirer.List('contentLevel',
                      message="At which hierarchy would you like to regenerate content?",
                      choices=[
                          'Regenerate Entire Course',
                          'Regenerate Chapter',
                          'Regenerate Specific Page',
                      ]),
    ]

    user_prompt = inquirer.prompt(content_level)

    if user_prompt != None:
        answer = user_prompt['contentLevel']

        if answer == 'Regenerate Entire Course':
            course_records = DB.query(Course).filter(Course.topic_id == topic_record.id).all()
            courses = [course.name for course in course_records]
            course_name = _select_content_item(courses)
            course = _get_item_by_name(course_name, course_records)

            return PageProcessor.regenerate_content(topic_record, course)

        elif answer == 'Regenerate Chapter':
            chapter_records = DB.query(Chapter).filter(Chapter.topic_id == topic_record.id).all()
            chapters = [chapter.name for chapter in chapter_records]
            chapter_name = _select_content_item(chapters)
            chapter = _get_item_by_name(chapter_name, chapter_records)

            return CourseCreator.regenerate_content(topic_record, chapter)

        elif answer == 'Regenerate Specific Page':
            page_records = DB.query(Page).filter(Page.topic_id == topic_record.id).all()
            pages = [page.name for page in page_records]
            page_name = _select_content_item(pages)
            page = _get_item_by_name(page_name, page_records)

            return CourseCreator.regenerate_content(topic_record, page)

        else:
            "You did not select any content. Exiting..."

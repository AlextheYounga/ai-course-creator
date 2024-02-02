from db.db import DB, Topic, Course, Chapter, Page
from src.creator.course_creator import CourseCreator
from termcolor import colored
import sys
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



def select_generate_content(topic_name: str):
    topic_record = DB.query(Topic).filter(Topic.name == topic_name).first()

    if not topic_record:
        print(colored("No topic found. Exiting...", "red"))
        sys.exit()


    content_level = [
        inquirer.List('contentLevel',
                      message="At which hierarchy would you like to regenerate content?",
                      choices=[
                          'Generate Specific Course',
                          'Generate Specific Chapter',
                          'Generate Specific Page',
                      ]),
    ]

    user_prompt = inquirer.prompt(content_level)

    if user_prompt != None:
        answer = user_prompt['contentLevel']

        if answer == 'Generate Specific Course':
            course_records = DB.query(Course).filter(Course.topic_id == topic_record.id).all()
            courses = [course.name for course in course_records]
            course_name = _select_content_item(courses)
            course = _get_item_by_name(course_name, course_records)

            return CourseCreator.generate_specific_course(topic_record, course)

        elif answer == 'Generate Specific Chapter':
            chapter_records = DB.query(Chapter).filter(Chapter.topic_id == topic_record.id).all()
            chapters = [chapter.name for chapter in chapter_records]
            chapter_name = _select_content_item(chapters)
            chapter = _get_item_by_name(chapter_name, chapter_records)

            return CourseCreator.generate_specific_chapter(topic_record, chapter)

        elif answer == 'Generate Specific Page':
            page_records = DB.query(Page).filter(Page.topic_id == topic_record.id).all()
            pages = [page.name for page in page_records]
            page_name = _select_content_item(pages)
            page = _get_item_by_name(page_name, page_records)

            CourseCreator.generate_specific_pages(topic_record, [page])

        else:
            "You did not select any content. Exiting..."

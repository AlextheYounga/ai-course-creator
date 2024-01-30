from db.db import DB, Topic, Course
import inquirer


def _get_item_by_name(name, items):
    for item in items:
        if item.name == name:
            return item

    raise Exception("You did not select an item. Exiting...")


def select_course(topic: Topic):
    course_records = DB.query(Course).filter(Course.topic_id == topic.id).all()
    course_choices = [course.name for course in course_records]


    course_select = [
        inquirer.List('courseSelect',
                      message="Which topic would you like to generate course material for?",
                      choices=course_choices),
    ]

    user_prompt = inquirer.prompt(course_select)

    if user_prompt != None:
        answer = user_prompt['courseSelect']
        course = _get_item_by_name(answer, course_records)
        return course

import inquirer
from db.db import DB, Topic, Outline
from .select_topic import select_topic
from .select_generate_content import select_generate_content
from services.openai_service import OpenAiService
from src.creator.course_creator import CourseCreator



def generate_outline(topic: Topic):
    creator = CourseCreator(OpenAiService, topic.name)
    return creator.create_outline()


def select_subroutine():
    topic_name = select_topic()
    topic = Topic.first_or_create(DB, name=topic_name)

    base_subroutines = {
        'Generate Outline': generate_outline,
        'Generate Content': select_generate_content,
    }

    subroutines = [
        inquirer.List('subroutine',
                      message="Select subroutine",
                      choices=list(base_subroutines.keys())),
    ]

    choice = inquirer.prompt(subroutines)
    subroutine = choice['subroutine']
    subroutine_function = base_subroutines[subroutine]

    # Dynamic function call
    subroutine_function(topic)
    print('Done')

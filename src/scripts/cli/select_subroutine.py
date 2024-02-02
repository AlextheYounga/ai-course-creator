import inquirer
from src.llm.openai_handler import OpenAiHandler
from .select_topic import select_topic
from .select_regenerate_content import select_regenerate_content
from .select_generate_content import select_generate_content
from .select_outline import select_outline
from src.creator.regenerator import Regenerator
from src.creator.course_creator import CourseCreator


def select_subroutine():
    choices = [
        inquirer.List('subroutine',
                      message="Select subroutine.",
                      choices=[
                          'Generate Course Outlines',
                          'Generate Course Pages',
                          'Generate Practice Skill Challenges',
                          'Generate Final Skill Challenges',
                          'Generate Specific Content',
                          'Regenerate Content',
                          'Run All',
                          'Dump Content From Existing Outline',
                      ]),
    ]

    choice = inquirer.prompt(choices)
    subroutine = choice['subroutine']


    if subroutine == 'Generate Course Outlines':
        topic_name = select_topic()
        creator = CourseCreator(OpenAiHandler, topic_name)
        return creator.create_outline()

    elif subroutine == 'Generate Course Pages':
        topic_name = select_topic()
        creator = CourseCreator(OpenAiHandler, topic_name)
        return creator.create_topic_page_material()

    elif subroutine == 'Generate Practice Skill Challenges':
        topic_name = select_topic()
        creator = CourseCreator(OpenAiHandler, topic_name)
        return creator.create_topic_practice_skill_challenges()

    elif subroutine == 'Generate Final Skill Challenges':
        topic_name = select_topic()
        creator = CourseCreator(OpenAiHandler, topic_name)
        return creator.create_topic_final_skill_challenges()

    elif subroutine == 'Generate Specific Content':
        topic_name = select_topic()
        return select_generate_content(topic_name)

    elif subroutine == 'Regenerate Content':
        topic_name = select_topic(include_all=False)
        content = select_regenerate_content(topic_name)
        return Regenerator.regenerate_content(content)

    elif subroutine == 'Run All':
        topic = select_topic()
        creator = CourseCreator(OpenAiHandler, topic_name)
        return creator.generate_topic_courses()

    elif subroutine == 'Dump Content From Existing Outline':
        topic = select_topic(include_all=False)
        outline = select_outline(topic)
        return CourseCreator.dump_outline_content(outline.id)

    else:
        "You did not select a subroutine. Exiting..."

import inquirer
from .select_topic import select_topic
from .select_regenerate_content import select_regenerate_content
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
                          'Run All',
                          'Dump Content From Existing Outline',
                          'Regenerate Content'
                      ]),
    ]

    choice = inquirer.prompt(choices)
    subroutine = choice['subroutine']


    if subroutine == 'Generate Course Outlines':
        topics = select_topic()
        return CourseCreator.create_outlines(topics)

    elif subroutine == 'Generate Course Pages':
        topics = select_topic()
        return CourseCreator.create_page_material(topics)

    elif subroutine == 'Generate Practice Skill Challenges':
        topics = select_topic()
        return CourseCreator.create_practice_skill_challenges(topics)

    elif subroutine == 'Generate Final Skill Challenges':
        topics = select_topic()
        return CourseCreator.create_final_skill_challenges(topics)

    elif subroutine == 'Run All':
        topics = select_topic()
        return CourseCreator.run_all(topics)

    elif subroutine == 'Dump Content From Existing Outline':
        topic = select_topic(include_all=False)
        outline = select_outline(topic)
        return CourseCreator.dump_outline_content(outline.id)

    elif subroutine == 'Regenerate Content':
        topic = select_topic(include_all=False)
        content = select_regenerate_content(topic)
        return Regenerator.regenerate_content(content)

    else:
        "You did not select a subroutine. Exiting..."

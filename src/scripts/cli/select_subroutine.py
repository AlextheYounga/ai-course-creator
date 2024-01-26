import inquirer
from .select_topic import select_topic
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
                      ]),
    ]

    choice = inquirer.prompt(choices)
    subroutine = choice['subroutine']

    topics = select_topic()

    if subroutine == 'Generate Course Outlines':
        return CourseCreator.create_outlines(topics)
    elif subroutine == 'Generate Course Pages':
        return CourseCreator.create_page_material(topics)
    elif subroutine == 'Generate Practice Skill Challenges':
        return CourseCreator.create_practice_skill_challenges(topics)
    elif subroutine == 'Generate Final Skill Challenges':
        return CourseCreator.create_final_skill_challenges(topics)
    elif subroutine == 'Run All':
        return CourseCreator.run_all(topics)

    else:
        "You did not select a subroutine. Exiting..."
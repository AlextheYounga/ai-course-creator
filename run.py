import inquirer
from src.utils.files import read_json_file


def main():
    choices = [
        inquirer.List('subroutine',
                      message="Select subroutine.",
                      choices=[
                          'Generate Course Outlines',
                          'Generate Course Pages',
                          'Generate Practice Skill Challenges',
                          'Run All',
                      ]),
    ]

    choice = inquirer.prompt(choices)
    answer = choice['subroutine']

    if answer == 'Generate Course Outlines':
        from src.openai.outlines.create_outlines import create_outlines
        create_outlines()
    elif answer == 'Generate Course Pages':
        from src.openai.page_material_creator import run_page_creator
        run_page_creator()
    elif answer == 'Generate Practice Skill Challenges':
        from src.openai.practice_skill_challenge_creator import run_practice_skill_challenge_creator
        run_practice_skill_challenge_creator()
    elif answer == 'Run All':
        topics = read_json_file("data/topics.json")
        from src.openai.outlines.create_outlines import process_topics
        from src.openai.page_material_creator import process_pages

        process_topics(topics)
        process_pages(topics)
    else:
        "You did not select a subroutine. Exiting..."


if __name__ == '__main__':
    main()

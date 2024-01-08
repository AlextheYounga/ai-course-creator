import inquirer
from src.utils.files import read_json_file


def prompt_user_for_topic():
    topics = read_json_file("data/topics.json")
    topic_choices = ['All'] + topics

    choices = [
        inquirer.List('topic',
                        message="Which topic would you like to generate practice skill challenges for?",
                        choices=topic_choices),
    ]

    choice = inquirer.prompt(choices)
    if choice != None:
        answer = choice['topic']
        return [answer]
    else:
        return topics

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
        from src.openai.outlines.create_outlines import cli_prompt_user
        cli_prompt_user()
    elif answer == 'Generate Course Pages':
        from src.openai.page_material_creator import cli_prompt_user
        cli_prompt_user()
    elif answer == 'Generate Practice Skill Challenges':
        from src.openai.practice_skill_challenge_creator import cli_prompt_user
        cli_prompt_user()
    elif answer == 'Run All':
        from src.openai.outlines.create_outlines import main as run_create_outlines
        from src.openai.page_material_creator import main as run_create_pages
        from src.openai.practice_skill_challenge_creator import main as run_create_practice_skill_challenges

        topics = prompt_user_for_topic()

        run_create_outlines(topics)
        run_create_pages(topics)
        run_create_practice_skill_challenges(topics)
    else:
        "You did not select a subroutine. Exiting..."


if __name__ == '__main__':
    main()

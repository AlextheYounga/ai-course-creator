import inquirer
from termcolor import colored
from src.utils.files import read_json_file
from server import run_server


def prompt_user_for_topic():
    try:
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
    except KeyboardInterrupt:
        print(colored("Exiting...", "red"))


def run_all():
    from src.openai.outlines.create_outlines import main as run_create_outlines
    from src.openai.page_material_creator import main as run_create_pages
    from src.openai.practice_skill_challenge_creator import main as run_create_practice_skill_challenges
    from src.openai.final_skill_challenge_creator import main as run_create_final_skill_challenges

    topics = prompt_user_for_topic()
    print(colored(f"Begin all topics course generation...", "yellow"))
    for topic in topics:
        print(colored(f"Begin generating {topic} course...", "yellow"))
        run_create_outlines([topic])
        run_create_pages([topic])
        run_create_practice_skill_challenges([topic])
        run_create_final_skill_challenges([topic])


def main():
    choices = [
        inquirer.List('subroutine',
                      message="Select subroutine.",
                      choices=[
                          'Generate Course Outlines',
                          'Generate Course Pages',
                          'Generate Practice Skill Challenges',
                          'Generate Final Skill Challenges',
                          'Run All',
                          'Run Server'
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
    elif answer == 'Generate Final Skill Challenges':
        from src.openai.final_skill_challenge_creator import cli_prompt_user
        cli_prompt_user()
    elif answer == 'Run All':
        run_all()
    elif answer == 'Run Server':
        run_server()

    else:
        "You did not select a subroutine. Exiting..."


if __name__ == '__main__':
    main()

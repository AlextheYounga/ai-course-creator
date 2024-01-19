import inquirer
from termcolor import colored
from src.utils.files import read_json_file
from src.openai.outlines.create_outlines import main as run_create_outlines
from src.openai.page_material_creator import main as run_create_pages
from src.openai.practice_skill_challenge_creator import main as run_create_practice_skill_challenges
from src.openai.final_skill_challenge_creator import main as run_create_final_skill_challenges


def _prompt_user_for_topic():
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
    topics = _prompt_user_for_topic()
    print(colored(f"Begin all topics course generation...", "yellow"))

    for topic in topics:
        print(colored(f"Begin generating {topic} course...", "yellow"))
        run_create_outlines([topic])
        run_create_pages([topic])
        run_create_practice_skill_challenges([topic])
        run_create_final_skill_challenges([topic])

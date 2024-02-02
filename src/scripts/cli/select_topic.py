from src.utils.files import read_json_file
import inquirer


def select_topic():
    topic_choices = read_json_file("storage/topics.json")

    choices = [
        inquirer.List('topic',
                      message="Which topic would you like to generate course material for?",
                      choices=topic_choices),
    ]

    choice = inquirer.prompt(choices)
    answer = choice['topic']

    return answer

from src.utils.files import read_yaml_file
import inquirer


def select_topic():
    topics_file = "storage/topics.yaml"
    topics = read_yaml_file(topics_file)
    topic_choices = list(topics['topics'].keys())

    choices = [
        inquirer.List('topic',
                      message="Which topic would you like to generate course material for?",
                      choices=topic_choices),
    ]

    choice = inquirer.prompt(choices)
    answer = choice['topic']

    return answer

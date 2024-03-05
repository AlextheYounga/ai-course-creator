from src.utils.files import read_yaml_file
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
import inquirer


def select_topic():
    topics_file = "storage/topics.yaml"
    ScanTopicsFileHandler({'topicsFile': topics_file}).handle()

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

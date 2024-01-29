from src.utils.files import read_json_file
from termcolor import colored
import inquirer


def select_topic(include_all: bool = True):
    topics = read_json_file("storage/topics.json")
    topic_choices = topics

    if include_all:
        topic_choices = ['All'] + topics


    choices = [
        inquirer.List('topic',
                      message="Which topic would you like to generate course material for?",
                      choices=topic_choices),
    ]

    choice = inquirer.prompt(choices)

    if choice != None:
        answer = choice['topic']

    if include_all:
        if answer == 'All':
            return topics
        else:
            return [answer]

    return answer

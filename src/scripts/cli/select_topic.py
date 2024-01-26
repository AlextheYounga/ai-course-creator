from src.utils.files import read_json_file
from termcolor import colored
import inquirer

def select_topic():
    try:
        topics = read_json_file("storage/topics.json")
        topic_choices = ['All'] + topics

        choices = [
            inquirer.List('topic',
                          message="Which topic would you like to generate practice skill challenges for?",
                          choices=topic_choices),
        ]

        choice = inquirer.prompt(choices)

        if choice != None:
            answer = choice['topic']
            
            if answer == 'All':
                return topics
            else:
                return answer

    except KeyboardInterrupt:
        print(colored("Exiting...", "red"))

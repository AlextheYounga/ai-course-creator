import inquirer
from .chat_utils import *

def select_util():
    choices = [
        inquirer.List('utils',
                      message="Select utility command.",
                      choices=[
                          'Save Chat',
                          'Reset Chat',
                          'Clear Logs'
                      ]),
    ]

    choice = inquirer.prompt(choices)
    answer = choice['utils']
    if answer == 'Reset Chat':
        reset_chat()
    elif answer == 'Clear Logs':
        clear_logs()
    elif answer == 'Save Chat':
        save_chat()
    else:
        "You did not select a utility command. Exiting..."

    print('Done.')
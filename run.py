import inquirer
from termcolor import colored
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
from src.scripts.cli.select_task import select_task
from src.scripts.cli.select_util import select_util
from src.scripts.cli.select_script import select_script
from src.scripts.initialize import initialize_project
from server import run_server


def main():
    initialize_project()

    ScanTopicsFileHandler().handle()

    try:
        choices = [
            inquirer.List('category',
                          message="Select command category",
                          choices=[
                              'Start Course Creator',
                              'Utilities',
                              'Scripts',
                              'Run App Server'
                          ]),
        ]

        choice = inquirer.prompt(choices)
        answer = choice['category']

        if answer == 'Start Course Creator':
            return select_task()
        elif answer == 'Utilities':
            return select_util()
        elif answer == 'Scripts':
            return select_script()
        elif answer == 'Run App Server':
            return run_server()
        else:
            "You did not select a command category. Exiting..."

        print('Done.')
    except KeyboardInterrupt:
        print(colored("Exiting...", "red"))



if __name__ == '__main__':
    main()

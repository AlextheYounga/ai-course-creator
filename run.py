import inquirer
from termcolor import colored
from src.scripts.cli.select.select_job import select_job
from src.scripts.cli.select.select_util import select_util
from src.scripts.initialize import initialize_project
from server import run_server


def main():
    initialize_project()

    try:
        choices = [
            inquirer.List('category',
                          message="Select command category",
                          choices=[
                              'Start Course Creator',
                              'Utilities',
                              'Run App Server'
                          ]),
        ]

        choice = inquirer.prompt(choices, raise_keyboard_interrupt=True)
        answer = choice['category']

        match answer:
            case 'Start Course Creator':
                return select_job()
            case 'Utilities':
                return select_util()
            case 'Run App Server':
                return run_server()
            case _:
                "You did not select a command category. Exiting..."

        print('Done.')
    except KeyboardInterrupt:
        print(colored("Exiting...", "red"))




if __name__ == '__main__':
    main()

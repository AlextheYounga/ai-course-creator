import inquirer
from src.scripts.cli.select_subroutine import select_subroutine
from src.scripts.cli.select_util import select_util
from src.scripts.initialize import initialize_project
from server import run_server


def main():
    choices = [
        inquirer.List('category',
                      message="Select command category",
                      choices=[
                          'Start Course Creator',
                          'Utilities',
                          'Initialize Project',
                          'Run App Server'
                      ]),
    ]

    choice = inquirer.prompt(choices)
    answer = choice['category']

    if answer == 'Start Course Creator':
        select_subroutine()
    elif answer == 'Utilities':
        select_util()
    elif answer == 'Initialize Project':
        initialize_project()
    elif answer == 'Run App Server':
        run_server()
    else:
        "You did not select a command category. Exiting..."

    print('Done.')


if __name__ == '__main__':
    main()

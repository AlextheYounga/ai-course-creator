import inquirer
import argparse
from termcolor import colored
from src.handlers.scan_topics_file_handler import ScanTopicsFileHandler
from src.scripts.cli.select.select_job import select_job
from src.scripts.cli.select.select_util import select_util
from src.scripts.cli.select.select_script import select_script
from src.scripts.initialize import initialize_project
from server import run_server


def parse_command_line_arguments():
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-t', '--topics', help='Topics file path', required=False, default="configs/topics.yaml")
    args = vars(parser.parse_args())

    return args


def main():
    initialize_project()

    cli_args = parse_command_line_arguments()
    topics_file = cli_args.get('topics', None)
    ScanTopicsFileHandler({'topicsFile': topics_file}).handle()

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

        choice = inquirer.prompt(choices, raise_keyboard_interrupt=True)
        answer = choice['category']

        match answer:
            case 'Start Course Creator':
                return select_job()
            case 'Utilities':
                return select_util()
            case 'Scripts':
                return select_script()
            case 'Run App Server':
                return run_server()
            case _:
                "You did not select a command category. Exiting..."

        print('Done.')
    except KeyboardInterrupt:
        print(colored("Exiting...", "red"))




if __name__ == '__main__':
    main()

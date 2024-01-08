import inquirer
from termcolor import colored
import os
import shutil
from datetime import datetime
from src.utils.chat_helpers import slugify
from src.utils.files import zip_folder

OUTPUT_PATH = 'out/course_material'
LOGS_PATH = 'data/logs'


def init():
    if not os.path.exists('./.env'):
        print(colored("Creating .env file...", "yellow"))
        shutil.copy('.env.example', '.env')

        print(colored("Project initialized.", "green"))
        print("Please add any sensitive information to the .env file.")
        return

    print(colored("Project already initialized.", "yellow"))


def save_chat():
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"chat-{timestamp}.zip"
    chat_name = None

    try:
        chat_name = inquirer.text(message="Enter chat name")
    except:
        print(f"No chat name provided. Using default {filename}")

    if chat_name:
        filename = f"chat-{slugify(chat_name)}.zip"

    # Copying logs file to out folder
    shutil.copy(f"{LOGS_PATH}/chat.log", "out/chat.log")

    zip_folder("out", f"{filename}")
    os.rename(filename, f"storage/{filename}")

    print(colored(f"Chat saved to {filename}", "green"))


def reset_chat():
    print(colored("Nuking chat...", "yellow"))
    if os.path.exists(OUTPUT_PATH):
        shutil.rmtree(OUTPUT_PATH)
    print(colored("Nuked", "green"))


def clear_logs():
    open(f"{LOGS_PATH}/chat.log", 'w').close()


def main():
    choices = [
        inquirer.List('utils',
                      message="Select utility command.",
                      choices=[
                          'Initialize Project',
                          'Save Chat',
                          'Reset Chat',
                          'Clear Logs'
                      ]),
    ]

    choice = inquirer.prompt(choices)
    answer = choice['utils']
    if answer == 'Initialize Project':
        init()
    elif answer == 'Reset Chat':
        reset_chat()
    elif answer == 'Clear Logs':
        clear_logs()
    elif answer == 'Save Chat':
        save_chat()
    else:
        "You did not select a subroutine. Exiting..."

    print('Done.')


if __name__ == '__main__':
    main()

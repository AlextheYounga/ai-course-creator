import inquirer
import os
from datetime import datetime
import shutil
from src.utils.files import zip_folder

PAYLOAD_PATH = 'src/data/chat/payloads'
CREATOR_PATH = 'src/data/chat/course_material'

def init():
    if not os.path.exists(PAYLOAD_PATH):
        print('Creating data/chat/payloads directory...')
        os.mkdir(PAYLOAD_PATH)
    if not os.path.exists(CREATOR_PATH):
        print('Creating data/chat/course_material directory...')
        os.mkdir(CREATOR_PATH)

    print("Project initialized.")


def save_chat():
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"chat-{timestamp}.zip"
    zip_folder("src/data/chat/", f"{filename}")
    os.rename(filename, f"storage/{filename}")


def reset_chat():
    print('Nuking chat...')
    shutil.rmtree(PAYLOAD_PATH)
    shutil.rmtree(CREATOR_PATH)
    init()
    

def main():
    choices = [
        inquirer.List('utils',
                      message="Select utility command.",
                      choices=[
                          'Initialize Project',
                          'Reset Chat',
                          'Save Chat'
                      ]),
    ]

    choice = inquirer.prompt(choices)
    answer = choice['utils']
    if answer == 'Initialize Project':
        init()
    elif answer == 'Reset Chat':
        reset_chat()
    elif answer == 'Save Chat':
        save_chat()
    else:
        "You did not select a subroutine. Exiting..."

    print('Done.')


if __name__ == '__main__':
    main()

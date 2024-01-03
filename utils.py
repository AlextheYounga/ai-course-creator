import inquirer
import os
import shutil
from datetime import datetime
from src.utils.chat_helpers import slugify
from src.utils.files import zip_folder

LOG_PATH = 'src/data/chat/logs'
COURSE_MATERIAL_PATH = 'src/data/chat/course_material'


def init():
    if not os.path.exists(LOG_PATH):
        print('Creating data/chat/payloads directory...')
        os.makedirs(LOG_PATH, exist_ok=True)
        open(f"{LOG_PATH}/chat.log", 'a').close()

    if not os.path.exists(COURSE_MATERIAL_PATH):
        print('Creating data/chat/course_material directory...')
        os.makedirs(COURSE_MATERIAL_PATH, exist_ok=True)

    print("Project initialized.")


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

    zip_folder("src/data/chat/", f"{filename}")
    os.rename(filename, f"storage/{filename}")
    
    print(f"Chat saved to {filename}")  


def reset_chat():
    print('Nuking chat...')
    shutil.rmtree(COURSE_MATERIAL_PATH)
    init()


def clear_logs():
    open(f"{LOG_PATH}/chat.log", 'w').close()


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

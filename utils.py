import inquirer
import os
from datetime import datetime
import shutil
from src.utils.files import zip_folder

def init():
    payload_path = 'src/data/chat/payloads'
    replies_path = 'src/data/chat/replies'

    if not os.path.exists(payload_path):
        print('Creating data/chat/payloads directory...')
        os.mkdir(payload_path)
    if not os.path.exists(replies_path):
        print('Creating data/chat/replies directory...')
        os.mkdir(replies_path)

    print("Project initialized.")

def save_chat():
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"chat-{timestamp}.zip"
    zip_folder("src/data/chat/", f"{filename}")
    os.rename(filename, f"storage/{filename}")

def reset_chat():
    print('Nuking chat...')
    payload_path = 'src/data/chat/payloads'
    replies_path = 'src/data/chat/replies'
    shutil.rmtree(payload_path)
    shutil.rmtree(replies_path)
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

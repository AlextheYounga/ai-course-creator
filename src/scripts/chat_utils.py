import inquirer
from termcolor import colored
from dotenv import load_dotenv
import os
import shutil
from datetime import datetime
from src.utils.strings import slugify
from src.utils.files import zip_folder

load_dotenv()
OUTPUT_PATH = os.environ.get("OUTPUT_DIRECTORY") or 'out'
LOGS_PATH = 'storage/logs'


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

    zip_folder(OUTPUT_PATH, f"{filename}")
    os.rename(filename, f"storage/chat/{filename}")

    print(colored(f"Chat saved to {filename}", "green"))


def reset_chat():
    print(colored("Nuking chat...", "yellow"))
    if os.path.exists(OUTPUT_PATH):
        shutil.rmtree(OUTPUT_PATH)
    print(colored("Nuked", "green"))


def clear_logs():
    if (os.path.exists(f"{LOGS_PATH}/chat.log")):
        os.remove(f"{LOGS_PATH}/chat.log")
    open(f"{LOGS_PATH}/chat.log", 'w').close()

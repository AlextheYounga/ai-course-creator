import inquirer
from termcolor import colored
from dotenv import load_dotenv
import os
import shutil
from datetime import datetime
from src.utils.strings import slugify
from src.utils.files import zip_folder
from db.db import Outline, Page
import yaml

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


def clear_logs():
    if (os.path.exists(f"{LOGS_PATH}/chat.log")):
        os.remove(f"{LOGS_PATH}/chat.log")
    open(f"{LOGS_PATH}/chat.log", 'w').close()


def dump_outline_content(outline: Outline):
    topic = outline.topic
    entities = Outline.get_entities()

    output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
    output_path = f"{output_directory}/{topic.slug}"

    for page in entities['pages']:
        if not page.content: continue
        # Write to file
        Page.dump_page([page])


    with open(f"{output_path}/{outline.name}/skills.yaml", 'w') as skills_file:
        skills_file.write(yaml.dump(outline.skills, sort_keys=False))
        skills_file.close()

    with open(f"{output_path}/{outline.name}/outline.yaml", 'w') as outline_file:
        outline_file.write(yaml.dump(outline.master_outline, sort_keys=False))
        outline_file.close()
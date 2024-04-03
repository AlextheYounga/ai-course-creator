import os
from datetime import datetime
import inquirer
import yaml
from termcolor import colored
import shutil
from db.db import DB, Topic
from src.utils.strings import slugify
from src.utils.files import zip_folder, zip_file


OUTPUT_PATH = os.environ.get("OUTPUT_DIRECTORY") or 'out'
DATABASE_PATH = 'db/database.db'
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
    shutil.copy(f"{LOGS_PATH}/app.log", "out/app.log")

    zip_folder(OUTPUT_PATH, filename)
    os.rename(filename, f"storage/chat/{filename}")

    print(colored(f"Chat saved to {filename}", "green"))


def backup_database():
    name = inquirer.text(message="Enter backup name (a date will automatically be appended)") or "database"

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"{name}-{timestamp}.db.zip"
    output_path = "storage/data/backups/database.db"

    # Copying logs file to out folder
    shutil.copy(DATABASE_PATH, output_path)
    zip_file(output_path, f"storage/data/backups/{filename}")

    # Delete the original file in storage folder
    os.remove(output_path)

    print(colored(f"Database saved to {filename}", "green"))


def clear_logs():
    if (os.path.exists(f"{LOGS_PATH}/app.log")):
        os.remove(f"{LOGS_PATH}/app.log")
    open(f"{LOGS_PATH}/app.log", 'w').close()


def sync_topics_file(topics_file='storage/topics.yaml'):
    topics = DB.query(Topic).all()
    topic_file_obj = {}

    for topic in topics:
        topic_file_obj[topic.name] = topic.properties

    with open(topics_file, 'w') as topics_file:
        topics_file.write(yaml.dump(topic_file_obj, sort_keys=False))
        topics_file.close()

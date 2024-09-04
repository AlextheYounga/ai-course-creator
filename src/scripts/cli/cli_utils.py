import os
from datetime import datetime
import inquirer
from termcolor import colored
import shutil
from db.db import DB
from src.utils.strings import slugify
from src.utils.files import zip_folder, zip_file

db = DB()

OUTPUT_PATH = os.environ.get("OUTPUT_DIRECTORY") or 'out'
DATABASE_PATH = 'db/database.db'
LOGS_PATH = 'storage/logs'


def backup_database():
    name = inquirer.text(message="Enter backup name (a date will automatically be appended)") or "database"

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"{name}-{timestamp}.db.zip"
    output_path = "storage/backups/database.db"

    # Copying logs file to out folder
    shutil.copy(DATABASE_PATH, output_path)
    zip_file(output_path, f"storage/backups/{filename}")

    # Delete the original file in storage folder
    os.remove(output_path)

    print(colored(f"Database saved to {filename}", "green"))


def clear_logs():
    if (os.path.exists(f"{LOGS_PATH}/app.log")):
        os.remove(f"{LOGS_PATH}/app.log")
    open(f"{LOGS_PATH}/app.log", 'w').close()

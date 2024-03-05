from termcolor import colored
import os
import shutil

LOGS_PATH = 'storage/logs'


def _create_env_file():
    if not os.path.exists('./.env'):
        print(colored("Creating .env file...", "yellow"))
        shutil.copy('.env.example', '.env')
        print("Created. Please add any sensitive information to the .env file.")
        return True
    return False



def _create_log_file():
    if (not os.path.exists(f"{LOGS_PATH}/app.log")):
        open(f"{LOGS_PATH}/app.log", 'w').close()
        return True
    return False


def initialize_project():
    initialized = _create_env_file()
    initialized = _create_log_file()

    if initialized:
        print(colored("Project initialized.", "green"))
        return

    print(colored("Project already initialized.", "yellow"))

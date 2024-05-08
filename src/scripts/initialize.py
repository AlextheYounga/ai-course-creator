from termcolor import colored
import os
import shutil


def _create_env_file():
    if not os.path.exists('.env'):
        print(colored("Creating .env file...", "yellow"))
        shutil.copy('.env.example', '.env')
        print("Created. Please add any sensitive information to the .env file.")
        return True
    return False


def _copy_params_file():
    if not os.path.exists('configs/params.yaml'):
        shutil.copy('configs/params.example.yaml', 'configs/params.yaml')
        return True
    return False


def _copy_topics_file():
    if not os.path.exists('configs/topics.yaml'):
        shutil.copy('configs/topics.example.yaml', 'configs/topics.yaml')
        return True
    return False


def initialize_project():
    initialized = _create_env_file()
    initialized = _copy_params_file()
    initialized = _copy_topics_file()

    if initialized:
        print(colored("Project initialized.", "green"))
        return

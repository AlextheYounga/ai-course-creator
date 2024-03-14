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
    if not os.path.exists('params.yaml'):
        shutil.copy('params.example.yaml', 'params.yaml')
        return True
    return False


def _copy_topics_file():
    if not os.path.exists('storage/topics.yaml'):
        shutil.copy('storage/topics.example.yaml', 'storage/topics.yaml')
        return True
    return False


def initialize_project():
    initialized = _create_env_file()
    initialized = _copy_params_file()
    initialized = _copy_topics_file()

    if initialized:
        print(colored("Project initialized.", "green"))
        return

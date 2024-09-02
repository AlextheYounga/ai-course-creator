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


def copy_params_file():
    params_file = os.path.join('configs', 'params.yaml')

    if ((not os.path.exists(params_file))):
        shutil.copyfile(os.path.join('configs', 'params.example.yaml'), params_file)
        return True
    return False


def initialize_project():
    initialized = _create_env_file()
    initialized = copy_params_file()

    if initialized:
        print(colored("Project initialized.", "green"))
        return

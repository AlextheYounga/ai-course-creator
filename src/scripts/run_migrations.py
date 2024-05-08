import os
import importlib
from termcolor import colored
import inquirer


def _select_migration():
    migration_files = os.listdir("db/migrations")
    migrations = [os.path.splitext(os.path.basename(f))[0] for f in migration_files if '__' not in f]
    migration_choices = ['All'] + migrations

    choices = [
        inquirer.List('migrations',
                      message="Select utility command",
                      choices=migration_choices),
    ]

    choice = inquirer.prompt(choices, raise_keyboard_interrupt=True)
    answer = choice['migrations']

    return answer


def run_all_db_migrations():
    for migration_file in os.listdir("db/migrations"):
        if '__' in migration_file: continue

        module_name = os.path.splitext(os.path.basename(migration_file))[0]
        print(colored(f"Migrating {module_name}...", "yellow"))

        migration_module = importlib.import_module(f"db.migrations.{module_name}")
        up = getattr(migration_module, "up")
        up()

        print(colored("Done.", "green"))


def run_db_migrations():
    migration_selected = _select_migration()
    if migration_selected == 'All':
        return run_all_db_migrations()
    else:
        migration_module = importlib.import_module(f"db.migrations.{migration_selected}")
        up = getattr(migration_module, "up")
        up()

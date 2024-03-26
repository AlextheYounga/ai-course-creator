import inquirer
from ..cli_utils import *
from src.utils.helpers import dump_outline_content
from db.db import DB, Topic
from .select_outline import select_outline
from .select_topic import select_topic
from ..run_migrations import run_db_migrations


def run_dump_outline_content():
    topic_name = select_topic()
    topic = DB.query(Topic).filter_by(name=topic_name).first()
    outline = select_outline(topic)
    return dump_outline_content(topic, outline)


def select_util():
    choices = [
        inquirer.List('utils',
                      message="Select utility command",
                      choices=[
                          'Backup Database',
                          'Dump Content From Existing Outline',
                          'Run DB Migrations',
                          'Sync Topics File',
                          'Save Chat',
                          'Clear Logs'
                      ]),
    ]

    choice = inquirer.prompt(choices)
    answer = choice['utils']
    if answer == 'Backup Database':
        return backup_database()
    elif answer == 'Dump Content From Existing Outline':
        return run_dump_outline_content()
    elif answer == 'Run DB Migrations':
        return run_db_migrations()
    elif answer == 'Sync Topics File':
        return sync_topics_file()
    elif answer == 'Save Chat':
        return save_chat()
    elif answer == 'Clear Logs':
        return clear_logs()
    else:
        "You did not select a utility command. Exiting..."

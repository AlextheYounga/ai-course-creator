import inquirer
from ..cli_utils import *
from src.utils.helpers import dump_outline_content
from db.db import DB, Topic
from .select_outline import select_outline
from .select_topic import select_topic
from ..translate_to_course_draft import translate_to_course_draft
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
                          'Dump Content From Existing Outline',
                          'Run DB Migrations',
                          'Backup Database',
                          'Save Chat',
                          'Clear Logs'
                      ]),
    ]

    choice = inquirer.prompt(choices)
    answer = choice['utils']
    if answer == 'Dump Content From Existing Outline':
        return run_dump_outline_content()
    elif answer == 'Run DB Migrations':
        return run_db_migrations()
    elif answer == 'Backup Database':
        return backup_database()
    elif answer == 'Save Chat':
        return save_chat()
    elif answer == 'Clear Logs':
        return clear_logs()
    elif answer == 'Run Draft Translations':
        return translate_to_course_draft()
    else:
        "You did not select a utility command. Exiting..."

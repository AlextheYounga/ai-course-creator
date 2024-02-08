import inquirer
from ..utils import *
from db.db import DB, Topic
from .select_outline import select_outline
from .select_topic import select_topic
from ..draft_translation import draft_translation


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
                          'Save Chat',
                          'Clear Logs',
                          'Run Draft Translations'
                      ]),
    ]

    choice = inquirer.prompt(choices)
    answer = choice['utils']
    if answer == 'Clear Logs':
        return clear_logs()
    elif answer == 'Save Chat':
        return save_chat()
    elif answer == 'Dump Content From Existing Outline':
        return run_dump_outline_content()
    elif answer == 'Run Draft Translations':
        return draft_translation()
    else:
        "You did not select a utility command. Exiting..."

    print('Done.')

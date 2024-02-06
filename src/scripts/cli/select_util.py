import inquirer
from ..utils import *
from db.db import DB, Topic
from .select_outline import select_outline
from .select_topic import select_topic


def run_dump_outline_content(topic: Topic):
    outline = topic.get_latest_outline()
    return dump_outline_content(outline)


def select_util():
    choices = [
        inquirer.List('utils',
                      message="Select utility command",
                      choices=[
                          'Save Chat',
                          'Clear Logs',
                          'Dump Content From Existing Outline',
                      ]),
    ]

    choice = inquirer.prompt(choices)
    answer = choice['utils']
    if answer == 'Clear Logs':
        clear_logs()
    elif answer == 'Save Chat':
        save_chat()
    elif answer == 'Dump Content From Existing Outline':
        topic_name = select_topic()
        topic = DB.query(Topic).filter_by(name=topic_name).first()
        outline = select_outline(topic)
        run_dump_outline_content(topic, outline)
    else:
        "You did not select a utility command. Exiting..."

    print('Done.')

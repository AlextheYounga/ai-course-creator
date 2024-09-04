import inquirer
from db.db import DB, Topic
from ..cli_utils import *
from .select_outline import select_outline
from .select_topic import select_topic
from src.scripts.run_migrations import run_db_migrations
from src.handlers.dump_outline_content_handler import DumpOutlineContentHandler

db = DB()


def run_dump_outline_content():
    topic_name = select_topic()
    topic = db.query(Topic).filter_by(name=topic_name).first()
    outline = select_outline(topic)

    return DumpOutlineContentHandler({
        'outlineId': outline.id,
        'topicId': topic.id
    }).handle()


def select_util():
    choices = [
        inquirer.List('utils',
                      message="Select utility command",
                      choices=[
                          'Backup Database',
                          'Dump Content From Existing Outline',
                          'Run DB Migrations',
                      ]),
    ]

    choice = inquirer.prompt(choices, raise_keyboard_interrupt=True)
    answer = choice['utils']

    match answer:
        case 'Backup Database':
            return backup_database()
        case 'Dump Content From Existing Outline':
            return run_dump_outline_content()
        case 'Run DB Migrations':
            return run_db_migrations()
        case _:
            return "You did not select a utility command. Exiting..."

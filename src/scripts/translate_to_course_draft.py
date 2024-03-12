import os
from ..mapping.map_courses_to_course_drafts import map_courses_to_course_drafts
from .cli.select_topic import select_topic
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models.course_draft import *
from termcolor import colored

DB_PATH = 'storage/drafts.db'


def _map_db_client(db_path: str):
    database_path = db_path
    engine = create_engine(database_path)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def translate_to_course_draft(db_path: str = f"sqlite:///{DB_PATH}"):
    # Reset output directory
    if (os.path.exists(DB_PATH)):
        os.remove(DB_PATH)

    print("\n")

    topic_name = select_topic()

    course_drafts = map_courses_to_course_drafts(topic_name)

    MAP_DB = _map_db_client(db_path)

    for draft in course_drafts:
        draft_record = CourseDraft(
            id=draft['id'],
            title=draft['title'],
            draftKey=draft['draftKey'],
            savedBy=draft['savedBy'],
            version=draft['version'],
            data=draft['data'],
        )
        MAP_DB.add(draft_record)

    MAP_DB.commit()

    print(colored("Draft translation complete", "green"))

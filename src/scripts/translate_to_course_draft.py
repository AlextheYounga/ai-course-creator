import os
from ..mapping.map_courses_to_course_drafts import map_courses_to_course_drafts
from .parse_content_nodes import parse_nodes_from_all_pages
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

    parse_nodes_from_all_pages()

    print("\n")

    course_drafts = map_courses_to_course_drafts()

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
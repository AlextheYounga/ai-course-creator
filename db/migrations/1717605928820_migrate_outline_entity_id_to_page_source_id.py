from sqlalchemy import text
from termcolor import colored
from db.db import DB, Interactive, OutlineEntity


db = DB()


def up():
    try:
        db.execute(text(
            """
            ALTER TABLE interactive
            RENAME COLUMN "outline_entity_id" TO "page_source_id";
            """
        ))

        db.commit()

        interactives = db.query(Interactive).all()
        for interactive in interactives:
            outline_entity = db.query(OutlineEntity).filter(OutlineEntity.id == interactive.page_source_id).first()
            page_id = outline_entity.entity_id

            interactive.page_source_id = page_id
            print(f"Migrated id: {interactive.id}, entity id {outline_entity.id} => page id {page_id}")
            db.commit()


    except Exception as e:
        db.rollback()
        print(colored(e, "red"))


db.close()

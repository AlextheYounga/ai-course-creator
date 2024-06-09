from sqlalchemy import text
from termcolor import colored
from db.db import DB, PageInteractive, Page


db = DB()


def up():
    try:
        pages = db.query(Page).all()
        for page in pages:
            if page.interactive_ids is None: continue
            for interactive_id in page.interactive_ids:
                page_interactive = PageInteractive(page_id=page.id, interactive_id=interactive_id)
                print(f"Migrated id: {page.id} => {interactive_id}")
                db.add(page_interactive)
                db.commit()


        db.execute(text(
            """
            ALTER TABLE page
            DROP COLUMN "interactive_ids";
            """
        ))

        db.commit()

    except Exception as e:
        db.rollback()
        print(colored(e, "red"))


db.close()

from sqlalchemy import text
from db.db import DB


def up():
    try:
        DB.execute(text(
            """
            ALTER TABLE outline 
            ADD COLUMN outline_chunks JSON;
            """
        ))

        DB.commit()

    except Exception as e:
        print(e)

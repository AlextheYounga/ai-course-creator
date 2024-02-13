from sqlalchemy import text
from termcolor import colored
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
        print(colored(e, "red"))

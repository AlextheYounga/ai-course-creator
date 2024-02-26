from sqlalchemy import text
from termcolor import colored
from db.db import DB


def up():
    try:
        DB.execute(text(
            """
            ALTER TABLE page 
            ADD COLUMN properties JSON;
            """
        ))

        DB.execute(text(
            """
            ALTER TABLE page
            ADD COLUMN active BOOLEAN DEFAULT TRUE;
            """
        ))

        DB.commit()

    except Exception as e:
        print(colored(e, "red"))

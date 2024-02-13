from sqlalchemy import text
from termcolor import colored
from db.db import DB


def up():
    try:
        DB.execute(text(
            """
            ALTER TABLE topic 
            ADD COLUMN master_outline_id integer
            AFTER id;
            """
        ))

        DB.commit()

    except Exception as e:
        print(colored(e, "red"))

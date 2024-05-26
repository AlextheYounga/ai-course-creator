from sqlalchemy import text
from termcolor import colored
from db.db import DB


# After running this, running python run.py should create the interactive table again
# These tables can be safely dropped as no data has ever been consistently stored in them

db = DB()


def up():
    try:
        # Remove question table
        db.execute(text(
            """
            DROP TABLE IF EXISTS question;
            """
        ))

        db.commit()


        # Remove answer table
        db.execute(text(
            """
            DROP TABLE IF EXISTS answer;
            """
        ))

        db.commit()

        # Remove interactive table
        db.execute(text(
            """
            DROP TABLE IF EXISTS interactive;
            """
        ))

        db.commit()

    except Exception as e:
        db.rollback()
        print(colored(e, "red"))


db.close()

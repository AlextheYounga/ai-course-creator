from db.db import *
from sqlalchemy import text


DB = db_client()


def truncate_tables():
    tables = Base.metadata.tables.keys()

    for table in tables:
        DB.execute(text(f"DELETE FROM {table}"))
        DB.commit()

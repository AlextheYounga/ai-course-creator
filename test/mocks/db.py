import os
from db.db import *
from sqlalchemy import text

try:
    os.remove('test/data/test.log')
except:
    pass

DB = db_client()


def truncate_tables():
    tables = Base.metadata.tables.keys()

    for table in tables:
        DB.execute(text(f"DELETE FROM {table}"))
        DB.commit()

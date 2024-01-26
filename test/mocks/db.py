import os
from db.db import *
from sqlalchemy import text

def truncate_tables(engine):
    tables = Base.metadata.tables.keys()

    for table in tables:
        engine.execute(text(f"DELETE FROM {table}"))
        engine.commit()


def setup_db():
    engine = db_client()
    
    truncate_tables(engine)

    return engine

DB = setup_db()
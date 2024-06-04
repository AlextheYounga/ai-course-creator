from db.db import *
import os
from sqlalchemy import text
import sqlite3
import zipfile


def truncate_tables():
    db = DB()
    tables = Base.metadata.tables.keys()

    for table in tables:
        db.execute(text(f"DELETE FROM {table}"))
        db.commit()

    db.close()  # Was getting flush warnings


def import_sql_data_from_file(db_path: str, sql_file_path: str, zipped: bool = False):
    # Step 1: Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Step 2: Open and read the SQL file
    sql_script = None
    if zipped:
        with zipfile.ZipFile(sql_file_path, 'r') as zip_ref:
            sql_file_dir = os.path.dirname(sql_file_path)
            sql_file_name = zip_ref.namelist()[0]

            zip_ref.extract(sql_file_name, sql_file_dir)

            with open(f"{sql_file_dir}/{sql_file_name}", 'r') as sql_file:
                sql_script = sql_file.read()

            os.remove(f"{sql_file_dir}/{sql_file_name}")
    else:
        with open(sql_file_path, 'r') as sql_file:
            sql_script = sql_file.read()

    # Step 3: Execute the SQL script
    cursor.executescript(sql_script)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

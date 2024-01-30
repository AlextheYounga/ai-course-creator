import os
from sqlalchemy import create_engine
from db.models import *
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


def db_client():
    load_dotenv()

    database_path = os.environ.get("DATABASE_URL") or 'sqlite:///db/database.db'
    engine = create_engine(database_path)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    return Session()


DB = db_client()

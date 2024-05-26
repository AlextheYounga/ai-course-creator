import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv
from db.models import *
from db.hooks import *


def create_session():
    load_dotenv()

    database_url = os.environ.get("DATABASE_URL") or 'sqlite:///db/database.db'
    engine = create_engine(database_url, pool_size=20, max_overflow=0)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)


# Create a global database session factory
DB = create_session()


# Function to get a session from the session factory
def get_session():
    return DB()


# Optional: Call this function at application startup to ensure the database engine is initialized
def init_db():
    database_url = os.environ.get("DATABASE_URL") or 'sqlite:///db/database.db'
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)

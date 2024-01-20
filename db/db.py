from sqlalchemy import create_engine
from db.models.chapter import *
from db.models.course import *
from db.models.page import *

from sqlalchemy.orm import sessionmaker

database_path = "sqlite:///db/database.db"
engine = create_engine(database_path)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
from sqlalchemy import Column, Integer, String, Date
from db.base import Base

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    hint = Column(String)
    created_at = Column(Date)
    updated_at = Column(Date)
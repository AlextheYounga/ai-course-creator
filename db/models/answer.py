from sqlalchemy import Column, Integer, String, Date
from db.base import Base

class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, nullable=False)
    value = Column(String, nullable=False)
    value_type = Column(String, nullable=False)
    created_at = Column(Date)
    updated_at = Column(Date)
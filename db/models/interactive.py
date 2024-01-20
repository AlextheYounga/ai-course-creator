from sqlalchemy import Column, Integer, String, JSON, Date
from db.base import Base

class Interactive(Base):
    __tablename__ = "interactives"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, nullable=False)
    answer_id = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    content = Column(JSON)
    created_at = Column(Date)
    updated_at = Column(Date)
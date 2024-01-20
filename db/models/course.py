from sqlalchemy import Column, Integer, String, JSON, Date
from db.base import Base

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    difficulty = Column(String)
    skill_challenge_chapter = Column(String)
    skill_challenge_total_questions = Column(Integer)
    meta = Column(JSON)
    created_at = Column(Date)
    updated_at = Column(Date)
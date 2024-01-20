from sqlalchemy import Column, Integer, String, JSON, Boolean, Date, Text
from db.base import Base

class Page(Base):
    __tablename__ = "pages"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, nullable=False)
    chapter_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    content = Column(Text)
    position = Column(Integer, nullable=False)
    created_at = Column(Date)
    updated_at = Column(Date)
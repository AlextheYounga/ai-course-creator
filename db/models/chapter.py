from sqlalchemy import Column, Integer, String, Date
from db.base import Base

class Chapter(Base):
    __tablename__ = "chapters"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    content_type = Column(String)   
    position = Column(Integer)
    created_at = Column(Date)
    updated_at = Column(Date)

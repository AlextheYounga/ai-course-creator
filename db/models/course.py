from .base import Base
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, relationship
from src.utils.strings import slugify


class Course(Base):
    __tablename__ = "course"
    id = mapped_column(Integer, primary_key=True)
    topic_id = mapped_column(ForeignKey("topic.id"))
    name = mapped_column(String, nullable=False)
    slug = mapped_column(String, nullable=False)
    level = mapped_column(Integer, nullable=False)
    outline = mapped_column(JSON)
    meta = mapped_column(JSON)
    skill_challenge_chapter = mapped_column(String)
    skill_challenge_total_questions = mapped_column(Integer)
    generated = mapped_column(Boolean)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    topic = relationship("Topic", back_populates="courses")

    def make_slug(name):
        return slugify(name)
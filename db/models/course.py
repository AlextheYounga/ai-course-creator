from .base import Base
from .topic import Topic
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, relationship
from src.utils.strings import slugify
from sqlalchemy.orm import Session


class Course(Base):
    __tablename__ = "course"
    id = mapped_column(Integer, primary_key=True)
    topic_id = mapped_column(ForeignKey("topic.id"))
    name = mapped_column(String, nullable=False)
    slug = mapped_column(String, nullable=False)
    level = mapped_column(Integer, nullable=False)
    meta = mapped_column(JSON)
    properties = mapped_column(JSON)
    generated = mapped_column(Boolean)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    topic = relationship("Topic", back_populates="courses")


    def make_slug(name):
        return slugify(name)


    def to_dict(self):
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "name": self.name,
            "slug": self.slug,
            "level": self.level,
            "meta": self.meta,
            "properties": self.properties,
            "generated": self.generated,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

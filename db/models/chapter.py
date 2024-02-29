from .base import Base
from .topic import Topic
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from src.utils.strings import slugify
from sqlalchemy.orm import Session



class Chapter(Base):
    __tablename__ = "chapter"
    id = mapped_column(Integer, primary_key=True)
    topic_id = mapped_column(ForeignKey("topic.id"))
    course_id = mapped_column(Integer, nullable=False, index=True)
    name = mapped_column(String, nullable=False)
    slug = mapped_column(String, nullable=False)
    content_type = mapped_column(String)
    position = mapped_column(Integer, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    topic = relationship("Topic", back_populates="chapters")

    def make_slug(name, course_slug):
        return slugify(name) if name != 'Final Skill Challenge' else f"final-skill-challenge-{course_slug}"


    def get_content_type(slug):
        if 'final-skill-challenge' in slug:
            return 'final-skill-challenge'

        if 'challenge' in slug:
            return 'challenge'

        return 'lesson'


    def to_dict(self):
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "course_id": self.course_id,
            "name": self.name,
            "slug": self.slug,
            "content_type": self.content_type,
            "position": self.position,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from src.utils.strings import slugify
from .base import Base


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


    @classmethod
    def make_slug(cls, name, course_slug):
        return slugify(name) if name != 'Final Skill Challenge' else f"final-skill-challenge-{course_slug}"


    @classmethod
    def get_content_type(cls, slug):
        if 'final-skill-challenge' in slug:
            return 'final-skill-challenge'

        if 'challenge' in slug:
            return 'challenge'

        return 'lesson'

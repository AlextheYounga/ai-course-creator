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
    course_slug = mapped_column(String, nullable=False)
    name = mapped_column(String, nullable=False)
    slug = mapped_column(String, nullable=False)
    outline = mapped_column(JSON)
    content_type = mapped_column(String)
    position = mapped_column(Integer, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    topic = relationship("Topic", back_populates="chapters")

    def make_slug(name, course_slug):
        return slugify(name) if name != 'Final Skill Challenge' else f"final-skill-challenge-{course_slug}"

    def to_dict(self):
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "course_slug": self.course_slug,
            "name": self.name,
            "slug": self.slug,
            "outline": self.outline,
            "content_type": self.content_type,
            "position": self.position,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


    @classmethod
    def first_or_create(self, session: Session, topic: Topic, data: dict):
        chapter_slug = self.make_slug(data['name'], data['courseSlug'])

        chapter = session.query(self).filter(
            self.topic_id == topic.id,
            self.slug == chapter_slug
        ).first()

        if not chapter:
            chapter = self(topic_id=topic.id)

        chapter.name = data['name']
        chapter.slug = chapter_slug
        chapter.course_slug = data['courseSlug']
        chapter.position = data['position']
        chapter.outline = data['outline']
        chapter.content_type = 'lesson' if data['name'] != 'Final Skill Challenge' else 'final-skill-challenge'

        return chapter

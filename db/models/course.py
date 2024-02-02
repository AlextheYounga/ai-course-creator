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


    def to_dict(self):
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "name": self.name,
            "slug": self.slug,
            "level": self.level,
            "outline": self.outline,
            "meta": self.meta,
            "skill_challenge_chapter": self.skill_challenge_chapter,
            "skill_challenge_total_questions": self.skill_challenge_total_questions,
            "generated": self.generated,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


    @classmethod
    def first_or_create(self, session: Session, topic: Topic, data: dict):
        course_slug = self.make_slug(data['name'])

        course = session.query(self).filter(
            self.topic_id == topic.id,
            self.slug == course_slug
        ).first()

        if not course:
            course = self(topic_id=topic.id)

        course.name = data['name']
        course.slug = course_slug
        course.level = data['position']
        course.outline = data['outline']
        course.skill_challenge_chapter = f"final-skill-challenge-{course_slug}"

        return course

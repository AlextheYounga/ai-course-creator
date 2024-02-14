from .base import Base
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import mapped_column, relationship
from src.utils.strings import slugify
from sqlalchemy.orm import Session



class Topic(Base):
    __tablename__ = "topic"
    id = mapped_column(Integer, primary_key=True)
    master_outline_id = mapped_column(Integer, nullable=True)
    name = mapped_column(String, nullable=False)
    slug = mapped_column(String, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    outlines = relationship(
        "Outline",
        back_populates="topic",
        cascade="all, delete-orphan"
    )
    courses = relationship(
        "Course",
        back_populates="topic",
        cascade="all, delete-orphan"
    )
    chapters = relationship(
        "Chapter",
        back_populates="topic",
        cascade="all, delete-orphan"
    )
    pages = relationship(
        "Page",
        back_populates="topic",
        cascade="all, delete-orphan"
    )

    def make_slug(name):
        return slugify(name)


    def to_dict(self):
        return {
            "id": self.id,
            "master_outline_id": self.master_outline_id,
            "name": self.name,
            "slug": self.slug,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


    def get_latest_outline(self):
        latest_outline = self.outlines[-1]
        return latest_outline


    @classmethod
    def first_or_create(self, session: Session, name: str):
        topic_record = session.query(Topic).filter(Topic.name == name).first()

        if not topic_record:
            topic_slug = Topic.make_slug(name)
            topic_record = Topic(name=name, slug=topic_slug)

            # Save topic to database
            session.add(topic_record)
            session.commit()

        return topic_record

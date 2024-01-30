from .base import Base
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import mapped_column, relationship
from src.utils.strings import slugify



class Topic(Base):
    __tablename__ = "topic"
    id = mapped_column(Integer, primary_key=True)
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
            "name": self.name,
            "slug": self.slug,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

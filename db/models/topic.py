import os
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, JSON
from sqlalchemy.orm import Session, mapped_column, relationship
from sqlalchemy.orm.attributes import flag_modified
from src.utils.strings import slugify
from .base import Base




class Topic(Base):
    __tablename__ = "topic"
    id = mapped_column(Integer, primary_key=True)
    master_outline_id = mapped_column(Integer, nullable=True)
    name = mapped_column(String, nullable=False)
    slug = mapped_column(String, nullable=False)
    properties = mapped_column(JSON)
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


    def to_dict(self):
        return {
            "id": self.id,
            "master_outline_id": self.master_outline_id,
            "name": self.name,
            "slug": self.slug,
            "properties": self.properties,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


    def get_latest_outline(self):
        latest_outline = self.outlines[-1]
        return latest_outline


    def get_properties(self, key=None):
        properties = self.properties or {}
        if key: return properties.get(key, {})

        return properties


    def update_properties(self, db: Session, properties: dict):
        self.properties = self.get_properties()
        self.properties.update(properties)
        flag_modified(self, 'properties')
        db.commit()

        return self

    @classmethod
    def make_slug(cls, name):
        return slugify(name)


    @classmethod
    def default_settings(cls):
        return {
            "settings": {
                "hasInteractives": True,
                "interactives": {
                    "codepen": False,
                    "counts": {
                        "lesson": 1,
                        "challenge": 5,
                        "final-skill-challenge": 20
                    },
                    "weights": {
                        "multipleChoice": 0.6,
                        "codeEditor": 0.2,
                        "codepen": 0.2
                    }
                }
            }
        }

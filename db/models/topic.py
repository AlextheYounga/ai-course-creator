from .base import Base
from src.utils.files import read_yaml_file
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, JSON
from sqlalchemy.orm import mapped_column, relationship
from src.utils.strings import slugify
from sqlalchemy.orm import Session



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

    def make_slug(name):
        return slugify(name)


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


    def get_properties(self):
        return self.properties or {}


    def get_settings(self, level: str = 'global'):
        properties = self.get_properties()
        settings = properties.get('settings', {})

        if level in settings:
            return settings.get(level, {})

        return settings.get('global', {})



    @classmethod
    def get_topic_properties_from_file(self, name: str):
        topics_data = read_yaml_file("storage/topics.yaml")
        topic = topics_data['topics'][name]
        if topic: return topic
        return {}


    @classmethod
    def first_or_create(self, DB: Session, name: str):
        topic_record = DB.query(self).filter(self.name == name).first()
        if topic_record: return topic_record

        topic_slug = self.make_slug(name)
        properties = self.get_topic_properties_from_file(name)

        new_topic_record = self(
            name=name,
            slug=topic_slug,
            properties=properties
        )

        # Save topic to database
        DB.add(new_topic_record)
        DB.commit()

        return new_topic_record

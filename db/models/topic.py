from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, JSON
from sqlalchemy.orm import Session, mapped_column, relationship
from sqlalchemy.orm.attributes import flag_modified
from src.utils.strings import slugify
from src.utils.files import read_yaml_file
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


    def get_settings(self, level: str = 'global'):
        properties = self.get_properties()
        settings = properties.get('settings', {})

        if level in settings:
            return settings.get(level, {})

        return settings.get('global', {})


    @classmethod
    def make_slug(cls, name):
        return slugify(name)


    @classmethod
    def get_topic_properties_from_file(cls, name: str):
        topics_data = read_yaml_file("configs/topics.yaml")
        topic = topics_data['topics'][name]
        if topic: return topic
        return {}


    @classmethod
    def first_or_create(cls, db: Session, name: str):
        topic_record = db.query(cls).filter(cls.name == name).first()
        if topic_record: return topic_record

        new_topic_record = cls(
            name=name,
            slug=cls.make_slug(name),
            properties=cls.get_topic_properties_from_file(name)
        )

        # Save topic to database
        db.add(new_topic_record)
        db.commit()

        return new_topic_record

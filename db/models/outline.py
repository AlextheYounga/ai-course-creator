import os
from .base import Base
from .topic import Topic
from .chapter import Chapter
from .course import Course
from .page import Page
from .outline_entity import OutlineEntity
from sqlalchemy.sql import func
from termcolor import colored
from sqlalchemy import Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from src.utils.files import read_yaml_file
from sqlalchemy.orm import Session
from src.utils.strings import string_hash
import yaml


class Outline(Base):
    __tablename__ = "outline"
    id = mapped_column(Integer, primary_key=True)
    topic_id = mapped_column(ForeignKey("topic.id"))
    name = mapped_column(String)
    hash = mapped_column(String, unique=True)
    outline_data = mapped_column(JSON)
    file_path = mapped_column(String)
    properties = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    topic = relationship("Topic", back_populates="outlines")

    entities = relationship(
        "OutlineEntity",
        back_populates="outline",
        cascade="all, delete-orphan"
    )


    def to_dict(self):
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "name": self.name,
            "hash": self.hash,
            "outline_data": self.outline_data,
            "file_path": self.file_path,
            "properties": self.properties,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


    @classmethod
    def get_master_outline(self, DB: Session, topic: Topic):
        if topic.master_outline_id:
            master_outline_record = DB.query(self).filter(
                self.topic_id == topic.id,
                self.id == topic.master_outline_id
            ).first()

            if master_outline_record: return master_outline_record

        return None



    @classmethod
    def import_outline(self, DB: Session, topic_id: int, outline_file: str):
        topic = DB.get(Topic, topic_id)

        outline_data = open(outline_file).read()
        outline_hash = self.hash_outline(outline_data)
        outline = DB.query(self).filter(self.hash == outline_hash).first()

        if outline:
            print(colored(f"Outline already exists with hash {outline_hash}", "red"))

        # Create new outline record
        new_outline = self.instantiate(DB, topic_id)
        new_outline.outline_data = read_yaml_file(outline_file)  # Add changed outline to record
        new_outline.hash = self.hash_outline(new_outline.outline_data)
        new_outline.file_path = outline_file

        DB.add(new_outline)
        DB.commit()
        print(colored(f"New outline created {new_outline.name}\n", "green"))

        topic.master_outline_id = new_outline.id
        DB.commit()
        print(colored(f"New master outline set {new_outline.id}\n", "green"))

        # Create outline entities
        self.create_outline_entities(DB, new_outline.id)

        return new_outline


    @staticmethod
    def hash_outline(outline_data):
        # Convert outline text to deterministic hash for comparison
        if isinstance(outline_data, dict) or isinstance(outline_data, list):
            outline_data = str(yaml.dump(outline_data, sort_keys=False)).strip()
        if isinstance(outline_data, str):
            outline_data = outline_data.strip()

        try:
            return string_hash(outline_data)
        except Exception:
            return None


    @staticmethod
    def get_entities_by_type(DB: Session, outline_id: int, type: str):
        if type == 'Course':
            return DB.query(Course).join(
                OutlineEntity, OutlineEntity.entity_id == Course.id
            ).filter(
                OutlineEntity.outline_id == outline_id,
                OutlineEntity.entity_type == type
            ).all()
        elif type == 'Chapter':
            return DB.query(Chapter).join(
                OutlineEntity, OutlineEntity.entity_id == Chapter.id
            ).filter(
                OutlineEntity.outline_id == outline_id,
                OutlineEntity.entity_type == type
            ).all()

        elif type == 'Page':
            return DB.query(Page).join(
                OutlineEntity, OutlineEntity.entity_id == Page.id
            ).filter(
                OutlineEntity.outline_id == outline_id,
                OutlineEntity.entity_type == type,
                Page.active == True,
            ).all()
        else:
            return None


    @staticmethod
    def get_entities(DB: Session, outline_id: int):
        return {
            'courses': DB.query(Course).join(
                OutlineEntity, OutlineEntity.entity_id == Course.id
            ).filter(
                OutlineEntity.outline_id == outline_id,
                OutlineEntity.entity_type == 'Course'
            ).all(),

            'chapters': DB.query(Chapter).join(
                OutlineEntity, OutlineEntity.entity_id == Chapter.id
            ).filter(
                OutlineEntity.outline_id == outline_id,
                OutlineEntity.entity_type == 'Chapter'
            ).all(),

            'pages': DB.query(Page).join(
                OutlineEntity, OutlineEntity.entity_id == Page.id
            ).filter(
                OutlineEntity.outline_id == outline_id,
                OutlineEntity.entity_type == 'Page',
                Page.active == True,
            ).all()
        }

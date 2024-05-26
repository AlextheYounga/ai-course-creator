from sqlalchemy.sql import func
from sqlalchemy import Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Session, mapped_column, relationship
from sqlalchemy.orm.attributes import flag_modified
import yaml
from src.utils.strings import string_hash
from .base import Base
from .topic import Topic
from .chapter import Chapter
from .course import Course
from .page import Page
from .outline_entity import OutlineEntity


class Outline(Base):
    __tablename__ = "outline"
    id = mapped_column(Integer, primary_key=True)
    topic_id = mapped_column(ForeignKey("topic.id"))
    name = mapped_column(String)
    hash = mapped_column(String, unique=True)
    outline_data = mapped_column(JSON)
    type = mapped_column(String)
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
            "type": self.type,
            "properties": self.properties,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


    def get_properties(self, key=None):
        properties = self.properties or {}
        if key: return properties.get(key, None)

        return properties


    def update_properties(self, db: Session, properties: dict):
        self.properties = self.get_properties()
        self.properties.update(properties)
        flag_modified(self, 'properties')
        db.commit()

        return self


    @classmethod
    def get_master_outline(cls, db: Session, topic: Topic):
        if topic.master_outline_id:
            master_outline_record = db.query(cls).filter(
                cls.topic_id == topic.id,
                cls.id == topic.master_outline_id
            ).first()

            if master_outline_record: return master_outline_record

        return None


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
    def get_entities_by_type(db: Session, outline_id: int, entity_type: str):
        match entity_type:
            case 'Course':
                return db.query(Course).join(
                    OutlineEntity, OutlineEntity.entity_id == Course.id
                ).filter(
                    OutlineEntity.outline_id == outline_id,
                    OutlineEntity.entity_type == entity_type
                ).all()
            case 'Chapter':
                return db.query(Chapter).join(
                    OutlineEntity, OutlineEntity.entity_id == Chapter.id
                ).filter(
                    OutlineEntity.outline_id == outline_id,
                    OutlineEntity.entity_type == entity_type
                ).all()

            case 'Page':
                return db.query(Page).join(
                    OutlineEntity, OutlineEntity.entity_id == Page.id
                ).filter(
                    OutlineEntity.outline_id == outline_id,
                    OutlineEntity.entity_type == entity_type,
                ).all()
            case _:
                return None


    @staticmethod
    def get_entities(db: Session, outline_id: int):
        return {
            'courses': db.query(Course).join(
                OutlineEntity, OutlineEntity.entity_id == Course.id
            ).filter(
                OutlineEntity.outline_id == outline_id,
                OutlineEntity.entity_type == 'Course'
            ).order_by(
                Course.level.asc()
            ).all(),

            'chapters': db.query(Chapter).join(
                OutlineEntity, OutlineEntity.entity_id == Chapter.id
            ).filter(
                OutlineEntity.outline_id == outline_id,
                OutlineEntity.entity_type == 'Chapter'
            ).all(),

            'pages': db.query(Page).join(
                OutlineEntity, OutlineEntity.entity_id == Page.id
            ).filter(
                OutlineEntity.outline_id == outline_id,
                OutlineEntity.entity_type == 'Page',
            ).all()
        }

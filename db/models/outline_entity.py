from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Session
from .base import Base



class OutlineEntity(Base):
    __tablename__ = "outline_entity"
    id = mapped_column(Integer, primary_key=True)
    outline_id = mapped_column(ForeignKey("outline.id"))
    entity_id = mapped_column(Integer, nullable=False, index=True)
    entity_type = mapped_column(String, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    outline = relationship("Outline", back_populates="entities")

    def to_dict(self):
        return {
            "id": self.id,
            "outline_id": self.outline_id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


    @classmethod
    def first_or_create(cls, db: Session, outline_id: int, entity):
        entity_record = db.query(cls).filter(
            cls.outline_id == outline_id,
            cls.entity_id == entity.id,
            cls.entity_type == type(entity).__name__
        ).first()

        if entity_record: return entity_record

        entity_record = cls(
            outline_id=outline_id,
            entity_id=entity.id,
            entity_type=type(entity).__name__
        )

        db.add(entity_record)
        db.commit()

        return entity_record


    @classmethod
    def create_entity(cls, db: Session, outline_id: int, entity):
        entity = cls(
            outline_id=outline_id,
            entity_id=entity.id,
            entity_type=type(entity).__name__
        )

        db.add(entity)
        db.commit()

        return entity


    @classmethod
    def create_entities(cls, db: Session, outline_id: int, entities: list):
        records = []

        for data in entities:
            entity = cls(
                outline_id=outline_id,
                entity_id=data.id,
                entity_type=type(data).__name__
            )

            db.add(entity)
            records.append(entity)

        db.commit()

        return records

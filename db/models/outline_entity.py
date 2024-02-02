from .base import Base
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship

from sqlalchemy.orm import Session



class OutlineEntity(Base):
    __tablename__ = "outline_entity"
    id = mapped_column(Integer, primary_key=True)
    outline_id = mapped_column(ForeignKey("outline.id"))
    entity_id = mapped_column(Integer, nullable=False)
    entity_type = mapped_column(String, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    outline = relationship("Outline", back_populates="entities")

    @classmethod
    def first_or_create(self, session: Session, outline_id: int, entity):
        entity_record = session.query(self).filter(
            self.outline_id == outline_id,
            self.entity_id == entity.id,
            self.entity_type == type(entity).__name__
        ).first()

        if entity_record: return entity_record

        entity_record = self(
            outline_id=outline_id,
            entity_id=entity.id,
            entity_type=type(entity).__name__
        )

        session.add(entity_record)
        session.commit()

        return entity_record


    @classmethod
    def create_entity(self, session: Session, outline_id: int, entity):
        entity = self(
            outline_id=outline_id,
            entity_id=entity.id,
            entity_type=type(entity).__name__
        )

        session.add(entity)
        session.commit()

        return entity


    @classmethod
    def create_entities(self, session: Session, outline_id: int, entities: list):
        records = []

        for data in entities:
            entity = self(
                outline_id=outline_id,
                entity_id=data.id,
                entity_type=type(data).__name__
            )

            session.add(entity)
            records.append(entity)

        session.commit()

        return records

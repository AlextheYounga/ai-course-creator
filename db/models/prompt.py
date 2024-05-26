from sqlalchemy.sql import func
from sqlalchemy import ForeignKey, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import Session, mapped_column, relationship
from sqlalchemy.orm.attributes import flag_modified
from .base import Base



class Prompt(Base):
    __tablename__ = "prompt"
    id = mapped_column(Integer, primary_key=True)
    outline_id = mapped_column(Integer, nullable=False, index=True)
    model = mapped_column(String, nullable=False)
    subject = mapped_column(String)
    estimated_tokens = mapped_column(Integer)
    content = mapped_column(Text, nullable=False)
    payload = mapped_column(JSON)
    attempts = mapped_column(Integer, default=0)
    properties = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    responses = relationship(
        "Response",
        back_populates="prompt",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "outline_id": self.outline_id,
            "model": self.model,
            "subject": self.subject,
            "estimated_tokens": self.estimated_tokens,
            "content": self.content,
            "payload": self.payload,
            "attempts": self.attempts,
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


    def increment_attempts(self, db: Session):
        attempts = self.attempts + 1

        if attempts > 3:
            raise Exception("Invalid response; maximum retries exceeded. Aborting...")

        self.attempts = attempts
        db.commit()

        return self

from .base import Base
from sqlalchemy.sql import func
from sqlalchemy import Boolean, Integer, String, DateTime, JSON
from sqlalchemy.orm import mapped_column, relationship



class Thread(Base):
    __tablename__ = "thread"
    id = mapped_column(Integer, primary_key=True)
    process_id = mapped_column(String, nullable=False)
    name = mapped_column(String)
    complete = mapped_column(Boolean, default=False)
    status = mapped_column(String)
    properties = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    prompts = relationship("Prompt", back_populates="thread")
    responses = relationship("Response", back_populates="thread")


    def to_dict(self):
        return {
            "id": self.id,
            "process_id": self.process_id,
            "name": self.name,
            "complete": self.complete,
            "status": self.status,
            "properties": self.properties,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

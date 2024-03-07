from .base import Base
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, JSON
from sqlalchemy.orm import mapped_column



class Event(Base):
    __tablename__ = "event"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, nullable=False)
    handler = mapped_column(String)
    data = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())


    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "handler": self.handler,
            "data": self.data,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

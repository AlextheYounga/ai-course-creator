from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, JSON
from sqlalchemy.orm import Session, mapped_column
from sqlalchemy.orm.attributes import flag_modified
from .base import Base


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


    def get_data(self):
        return self.data or {}


    def update_data(self, db: Session, data: dict):
        self.data = self.get_data()
        self.data.update(data)
        flag_modified(self, 'data')
        db.commit()

        return self

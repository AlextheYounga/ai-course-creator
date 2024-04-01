import os
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, JSON
from sqlalchemy.orm import Session, mapped_column, relationship
from sqlalchemy.orm.attributes import flag_modified
from .base import Base



class Thread(Base):
    __tablename__ = "thread"
    id = mapped_column(Integer, primary_key=True)
    pid = mapped_column(String, nullable=False)
    name = mapped_column(String)
    status = mapped_column(String, default="started")
    properties = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    prompts = relationship("Prompt", back_populates="thread")
    responses = relationship("Response", back_populates="thread")


    def to_dict(self):
        return {
            "id": self.id,
            "pid": self.pid,
            "name": self.name,
            "status": self.status,
            "properties": self.properties,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


    def get_properties(self):
        return self.properties or {}


    def set_complete(self, db: Session):
        self.status = "completed"
        db.commit()

        return self


    def update_properties(self, db: Session, properties: dict):
        self.properties = self.get_properties()
        self.properties.update(properties)
        flag_modified(self, 'properties')
        db.commit()

        return self


    @staticmethod
    def first_or_create(event_name: str, db: Session):
        pid = os.getpid()
        running_thread = db.query(Thread).filter(
            Thread.pid == pid
        ).first()

        if running_thread:
            return running_thread

        return Thread.start(db, event_name)


    @staticmethod
    def start(db: Session, event_name: str):
        pid = os.getpid()

        thread = Thread(
            name=event_name,
            pid=pid
        )

        db.add(thread)
        db.commit()

        return thread

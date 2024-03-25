import os
from .base import Base
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, JSON
from sqlalchemy.orm import Session
from sqlalchemy.orm import mapped_column, relationship



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

    @staticmethod
    def first_or_create(event_name: str, session: Session):
        pid = os.getpid()
        running_thread = session.query(Thread).filter(
            Thread.pid == pid
        ).first()

        if running_thread:
            return running_thread

        return Thread.start(event_name, session)


    @staticmethod
    def start(event_name: str, session: Session):
        pid = os.getpid()

        thread = Thread(
            name=event_name,
            pid=pid
        )

        session.add(thread)
        session.commit()

        return thread

    def set_complete(self, session: Session):
        self.status = "completed"
        session.commit()

        return self

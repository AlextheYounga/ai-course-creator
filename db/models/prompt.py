from .base import Base
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Session



class Prompt(Base):
    __tablename__ = "prompt"
    id = mapped_column(Integer, primary_key=True)
    thread_id = mapped_column(Integer, ForeignKey("thread.id"))
    outline_id = mapped_column(Integer, nullable=False, index=True)
    model = mapped_column(String, nullable=False)
    action = mapped_column(String)
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

    thread = relationship("Thread", back_populates="prompts")

    def to_dict(self):
        return {
            "id": self.id,
            "model": self.model,
            "action": self.action,
            "estimated_tokens": self.estimated_tokens,
            "content": self.content,
            "payload": self.payload,
            "properties": self.properties,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


    def increment_attempts(self, session: Session):
        self.attempts += 1
        session.commit()

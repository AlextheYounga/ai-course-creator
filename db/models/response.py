from .base import Base
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import mapped_column, relationship



class Response(Base):
    __tablename__ = "response"
    id = mapped_column(Integer, primary_key=True)
    thread_id = mapped_column(ForeignKey("thread.id"))
    prompt_id = mapped_column(ForeignKey("prompt.id"))
    outline_id = mapped_column(Integer, nullable=False, index=True)
    role = mapped_column(String)
    model = mapped_column(String)
    completion_tokens = mapped_column(Integer)
    prompt_tokens = mapped_column(Integer)
    total_tokens = mapped_column(Integer)
    content = mapped_column(Text)
    payload = mapped_column(JSON)
    properties = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    prompt = relationship("Prompt", back_populates="responses")
    thread = relationship("Thread", back_populates="responses")

    def to_dict(self):
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "prompt_id": self.prompt_id,
            "outline_id": self.outline_id,
            "role": self.role,
            "model": self.model,
            "completion_tokens": self.completion_tokens,
            "prompt_tokens": self.prompt_tokens,
            "total_tokens": self.total_tokens,
            "content": self.content,
            "payload": self.payload,
            "properties": self.properties,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

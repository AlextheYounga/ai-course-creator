from .base import Base
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import mapped_column, relationship



class Response(Base):
    __tablename__ = "response"
    id = mapped_column(Integer, primary_key=True)
    prompt_id = mapped_column(ForeignKey("prompt.id"))
    role = mapped_column(String, nullable=False)
    model = mapped_column(String, nullable=False)
    completion_tokens = mapped_column(Integer)
    prompt_tokens = mapped_column(Integer)
    total_tokens = mapped_column(Integer)
    content = mapped_column(Text, nullable=False)
    payload = mapped_column(JSON)
    properties = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    prompt = relationship("Prompt", back_populates="responses")

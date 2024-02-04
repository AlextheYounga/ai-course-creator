from .base import Base
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import mapped_column, relationship



class Prompt(Base):
    __tablename__ = "prompt"
    id = mapped_column(Integer, primary_key=True)
    model = mapped_column(String, nullable=False)
    action = mapped_column(String)
    estimated_tokens = mapped_column(Integer)
    content = mapped_column(Text, nullable=False)
    payload = mapped_column(JSON)
    properties = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    responses = relationship(
        "Response",
        back_populates="prompt",
        cascade="all, delete-orphan"
    )

from .base import Base
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, relationship



class Answer(Base):
    __tablename__ = "answer"
    id = mapped_column(Integer, primary_key=True)
    question_id = mapped_column(ForeignKey("question.id"))
    value = mapped_column(String, nullable=False)
    value_type = mapped_column(String, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    question = relationship("Question", back_populates="answer")
    interactives = relationship(
        "Interactive",
        back_populates="answer",
        cascade="all, delete-orphan"
    )

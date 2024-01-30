from .base import Base
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship



class Interactive(Base):
    __tablename__ = "interactive"
    id = mapped_column(Integer, primary_key=True)
    question_id = mapped_column(ForeignKey("question.id"))
    answer_id = mapped_column(ForeignKey("answer.id"))
    type = mapped_column(String, nullable=False)
    content = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    question = relationship("Question", back_populates="interactives")
    answer = relationship("Answer", back_populates="interactives")

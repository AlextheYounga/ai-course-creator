from sqlalchemy.sql import func
from sqlalchemy import Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from .base import Base


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

    def to_dict(self):
        return {
            "id": self.id,
            "question_id": self.question_id,
            "answer_id": self.answer_id,
            "type": self.type,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def save(cls, session, question_id, answer_id, interactive_type, content):
        interactive = cls(
            question_id=question_id,
            answer_id=answer_id,
            type=interactive_type,
            content=content
        )

        session.add(interactive)
        session.commit()

        return interactive

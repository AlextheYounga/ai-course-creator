from .base import Base
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Session



class Question(Base):
    __tablename__ = "question"
    id = mapped_column(Integer, primary_key=True)
    question = mapped_column(String, nullable=False)
    hint = mapped_column(String)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    interactives = relationship(
        "Interactive",
        back_populates="question",
        cascade="all, delete-orphan"
    )
    answer = relationship("Answer", back_populates="question")

    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "hint": self.hint,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def save(self, session: Session, question):
        question = self(
            question=question,
            hint=None,
        )

        session.add(question)
        session.commit()

        return question

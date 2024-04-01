from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Session
from .base import Base



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

    def to_dict(self):
        return {
            "id": self.id,
            "question_id": self.question_id,
            "value": self.value,
            "value_type": self.value_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


    @classmethod
    def save(cls, db: Session, question_id: int, value: str):
        answer = cls(
            question_id=question_id,
            value=value,
            value_type=type(value).__name__
        )

        db.add(answer)
        db.commit()

        return answer

from typing import List
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, JSON, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from src.utils.strings import timestamp_id, slugify, string_hash


class Base(DeclarativeBase):
    pass


class Outline(Base):
    __tablename__ = "outline"
    id = mapped_column(Integer, primary_key=True)
    topic_id = mapped_column(ForeignKey("topic.id"))
    name = mapped_column(String)
    hash = mapped_column(String, unique=True)
    skills = mapped_column(JSON)
    master_outline = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    topic: Mapped["Topic"] = relationship("Topic", back_populates="outlines")


class Course(Base):
    __tablename__ = "course"
    id = mapped_column(Integer, primary_key=True)
    topic_id = mapped_column(ForeignKey("topic.id"))
    name = mapped_column(String, nullable=False)
    slug = mapped_column(String, nullable=False)
    level = mapped_column(Integer, nullable=False)
    outline = mapped_column(JSON)
    meta = mapped_column(JSON)
    skill_challenge_chapter = mapped_column(String)
    skill_challenge_total_questions = mapped_column(Integer)
    generated = mapped_column(Boolean)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    topic: Mapped["Topic"] = relationship("Topic", back_populates="courses")

    def make_slug(name):
        return slugify(name)


class Chapter(Base):
    __tablename__ = "chapter"
    id = mapped_column(Integer, primary_key=True)
    topic_id = mapped_column(ForeignKey("topic.id"))
    course_slug = mapped_column(String, nullable=False)
    name = mapped_column(String, nullable=False)
    slug = mapped_column(String, nullable=False)
    outline = mapped_column(JSON)
    content_type = mapped_column(String)
    position = mapped_column(Integer, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    topic: Mapped["Topic"] = relationship("Topic", back_populates="chapters")

    def make_slug(name, course_slug):
        return slugify(name) if name != 'Final Skill Challenge' else f"final-skill-challenge-{course_slug}"


class Page(Base):
    __tablename__ = "page"
    id = mapped_column(Integer, primary_key=True)
    topic_id = mapped_column(ForeignKey("topic.id"))
    course_slug = mapped_column(String, nullable=False)
    chapter_slug = mapped_column(String, nullable=False)
    name = mapped_column(String, nullable=False)
    slug = mapped_column(String, nullable=False)
    permalink = mapped_column(String)
    link = mapped_column(String)
    path = mapped_column(String)
    hash = mapped_column(String, unique=True)
    type = mapped_column(String)
    content = mapped_column(Text)
    summary = mapped_column(Text)
    nodes = mapped_column(JSON)
    position = mapped_column(Integer, nullable=False)
    position_in_course = mapped_column(Integer, nullable=False)
    position_in_series = mapped_column(Integer, nullable=False)
    generated = mapped_column(Boolean, default=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    topic: Mapped["Topic"] = relationship("Topic", back_populates="pages")

    def make_slug(name, course_slug, chapter_slug):
        if name == 'Practice Skill Challenge':
            return f"challenge-{chapter_slug}"
        if 'Final Skill Challenge' in name:
            return f"{course_slug}-{slugify(name)}"
        return slugify(name)


class Answer(Base):
    __tablename__ = "answer"
    id = mapped_column(Integer, primary_key=True)
    question_id = mapped_column(ForeignKey("question.id"))
    value = mapped_column(String, nullable=False)
    value_type = mapped_column(String, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    question: Mapped["Question"] = relationship("Question", back_populates="answer")
    interactives: Mapped[List["Interactive"]] = relationship(
        back_populates="answer", cascade="all, delete-orphan"
    )


class Interactive(Base):
    __tablename__ = "interactive"
    id = mapped_column(Integer, primary_key=True)
    question_id = mapped_column(ForeignKey("question.id"))
    answer_id = mapped_column(ForeignKey("answer.id"))
    type = mapped_column(String, nullable=False)
    content = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    question: Mapped["Question"] = relationship("Question", back_populates="interactives")
    answer: Mapped["Answer"] = relationship("Answer", back_populates="interactives")



class Question(Base):
    __tablename__ = "question"
    id = mapped_column(Integer, primary_key=True)
    question = mapped_column(String, nullable=False)
    hint = mapped_column(String)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    interactives: Mapped[List["Interactive"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )
    answer: Mapped["Answer"] = relationship("Answer", back_populates="question")


class Topic(Base):
    __tablename__ = "topic"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, nullable=False)
    slug = mapped_column(String, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    outlines: Mapped[List["Outline"]] = relationship(
        "Outline",
        back_populates="topic",
        cascade="all, delete-orphan"
    )
    courses: Mapped[List["Course"]] = relationship(
        "Course",
        back_populates="topic",
        cascade="all, delete-orphan"
    )
    chapters: Mapped[List["Chapter"]] = relationship(
        "Chapter",
        back_populates="topic",
        cascade="all, delete-orphan"
    )
    pages: Mapped[List["Page"]] = relationship(
        "Page",
        back_populates="topic",
        cascade="all, delete-orphan"
    )

    def make_slug(name):
        return slugify(name)

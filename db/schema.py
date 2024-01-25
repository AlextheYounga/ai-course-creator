from typing import List
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, JSON, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from src.utils.strings import timestamp_id


class Base(DeclarativeBase):
    pass


class Outline(Base):
    __tablename__ = "outline"
    id = mapped_column(Integer, primary_key=True)
    topic_id = mapped_column(ForeignKey("topic.id"))
    name = mapped_column(String)
    hash = mapped_column(String, unique=True)
    skills = mapped_column(JSON)
    draft_outline = mapped_column(JSON)
    master_outline = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    topic: Mapped["Topic"] = relationship("Topic", back_populates="outlines")

    def instantiate(topic: Mapped["Topic"]):
        time_id = timestamp_id()
        outline_name = f"series-{time_id}"

        return Outline(
            topic_id=topic.id,
            name=outline_name
        )


class Page(Base):
    __tablename__ = "page"
    id = mapped_column(Integer, primary_key=True)
    topic_id = mapped_column(ForeignKey("topic.id"))
    name = mapped_column(String, nullable=False)
    course_slug = mapped_column(String, nullable=False)
    chapter_slug = mapped_column(String, nullable=False)
    slug = mapped_column(String, nullable=False)
    permalink = mapped_column(String)
    link = mapped_column(String)
    hash = mapped_column(String, unique=True)
    type = mapped_column(String)
    content = mapped_column(Text)
    summary = mapped_column(Text)
    nodes = mapped_column(JSON)
    course_data = mapped_column(JSON)
    position = mapped_column(Integer, nullable=False)
    position_in_series = mapped_column(Integer, nullable=False)
    position_in_course = mapped_column(Integer, nullable=False)
    generated = mapped_column(Boolean, default=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    topic: Mapped["Topic"] = relationship("Topic", back_populates="pages")


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
    pages: Mapped[List["Page"]] = relationship(
        "Page",
        back_populates="topic",
        cascade="all, delete-orphan"
    )

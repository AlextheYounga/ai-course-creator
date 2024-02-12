import os
from .base import Base
from .topic import Topic
from .chapter import Chapter
from .course import Course
from .page import Page
from .outline_entity import OutlineEntity
from sqlalchemy.sql import func, text
from termcolor import colored
from sqlalchemy import Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from src.utils.files import read_yaml_file
from sqlalchemy.orm import Session
from src.utils.strings import string_hash
import yaml


class Outline(Base):
    __tablename__ = "outline"
    id = mapped_column(Integer, primary_key=True)
    topic_id = mapped_column(ForeignKey("topic.id"))
    name = mapped_column(String)
    hash = mapped_column(String, unique=True)
    skills = mapped_column(JSON)
    outline_chunks = mapped_column(JSON)
    master_outline = mapped_column(JSON)
    file_path = mapped_column(String)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    topic = relationship("Topic", back_populates="outlines")

    entities = relationship(
        "OutlineEntity",
        back_populates="outline",
        cascade="all, delete-orphan"
    )


    def to_dict(self):
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "name": self.name,
            "hash": self.hash,
            "skills": self.skills,
            "outline_chunks": self.outline_chunks,
            "master_outline": self.master_outline,
            "file_path": self.file_path,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


    @classmethod
    def instantiate(self, session: Session, topic_id: int):
        existing_outline_count = session.query(self).filter(self.topic_id == topic_id).count()
        next_outline_number = str(existing_outline_count + 1)
        outline_name = f"series-{next_outline_number}"

        new_outline = self(
            topic_id=topic_id,
            name=outline_name
        )

        return new_outline


    @classmethod
    def get_or_create_from_file(self, session: Session, topic_id: int, outline_file: str | None = None):
        # outline_file: str
        if not outline_file:
            topic = session.get(Topic, topic_id)
            outline_file = self.default_outline_file_path(topic)

        outline_data = open(outline_file).read()
        outline_hash = self.hash_outline(outline_data)
        outline = session.query(self).filter(self.hash == outline_hash).first()
        if outline: return outline

        # Create new outline record
        last_outline = session.query(self).filter(
            Outline.topic_id == topic_id
        ).order_by(
            Outline.id.desc()
        ).first()

        new_outline = self.instantiate(session, topic_id)
        new_outline.master_outline = read_yaml_file(outline_file)  # Add changed outline to record
        new_outline.hash = self.hash_outline(new_outline.master_outline)
        new_outline.file_path = outline_file

        if last_outline:
            new_outline.skills = last_outline.skills

        print(colored("Detected new outline. Processing...", "yellow"))
        session.add(new_outline)
        session.commit()
        print(colored(f"New outline created {new_outline.name}\n", "green"))

        return new_outline


    @classmethod
    def create_outline_entities(self, session: Session, outline_id: int):
        outline = session.get(self, outline_id)
        topic = outline.topic

        if not outline: return None

        pages = []

        for course_index, course in enumerate(outline.master_outline):
            page_position_in_course = 0
            course = course['course']

            # Building course record
            course_record = Course.first_or_create(session, outline.topic, {
                'name': course['courseName'],
                'position': course_index,
                'outline': yaml.dump(course, sort_keys=False),
            })
            session.add(course_record)

            for chapter_index, chapter in enumerate(course['chapters']):
                # Building chapter record
                chapter_record = Chapter.first_or_create(
                    session,
                    topic,
                    {
                        'name': chapter['name'],
                        'courseSlug': course_record.slug,
                        'position': chapter_index,
                        'outline': yaml.dump(chapter, sort_keys=False),
                    })
                session.add(chapter_record)

                # Building page record
                for page_index, page in enumerate(chapter['pages']):
                    page_record = Page.first_or_create(
                        session,
                        topic,
                        {
                            'name': page,
                            'outlineName': outline.name,
                            'courseSlug': course_record.slug,
                            'chapterSlug': chapter_record.slug,
                            'position': page_index,
                            'positionInCourse': page_position_in_course,
                            'positionInSeries': len(pages),
                        })
                    session.add(page_record)
                    page_position_in_course += 1

                    # Saving to the database
                    session.commit()
                    pages.append(page_record)

                    # Create outline entities
                    OutlineEntity.first_or_create(session, outline.id, page_record)
                OutlineEntity.first_or_create(session, outline.id, chapter_record)
            OutlineEntity.first_or_create(session, outline.id, course_record)

        return pages


    @classmethod
    def process_outline(self, session: Session, topic_id: int, outline_file: str | None = None):
        outline = self.get_or_create_from_file(session, topic_id, outline_file)
        self.create_outline_entities(session, outline.id)

        return outline


    @staticmethod
    def hash_outline(outline_data):
        # Convert outline text to deterministic hash for comparison
        if isinstance(outline_data, dict) or isinstance(outline_data, list):
            outline_data = str(yaml.dump(outline_data, sort_keys=False)).strip()
        if isinstance(outline_data, str):
            outline_data = outline_data.strip()

        try:
            return string_hash(outline_data)
        except Exception:
            return None


    @staticmethod
    def get_entities_by_type(session: Session, outline_id: int, type: str):
        if type == 'Course':
            return session.query(Course).join(
                OutlineEntity, OutlineEntity.entity_id == Course.id
            ).filter(
                OutlineEntity.outline_id == outline_id,
                OutlineEntity.entity_type == type
            ).all()
        elif type == 'Chapter':
            return session.query(Chapter).join(
                OutlineEntity, OutlineEntity.entity_id == Chapter.id
            ).filter(
                OutlineEntity.outline_id == outline_id,
                OutlineEntity.entity_type == type
            ).all()

        elif type == 'Page':
            return session.query(Page).join(
                OutlineEntity, OutlineEntity.entity_id == Page.id
            ).filter(
                OutlineEntity.outline_id == outline_id,
                OutlineEntity.entity_type == type
            ).all()
        else:
            return None


    @staticmethod
    def get_entities(session: Session, outline_id: int):
        return {
            'courses': session.query(Course).join(
                OutlineEntity, OutlineEntity.entity_id == Course.id
            ).filter(
                OutlineEntity.outline_id == outline_id,
                OutlineEntity.entity_type == 'Course'
            ).all(),

            'chapters': session.query(Chapter).join(
                OutlineEntity, OutlineEntity.entity_id == Chapter.id
            ).filter(
                OutlineEntity.outline_id == outline_id,
                OutlineEntity.entity_type == 'Chapter'
            ).all(),

            'pages': session.query(Page).join(
                OutlineEntity, OutlineEntity.entity_id == Page.id
            ).filter(
                OutlineEntity.outline_id == outline_id,
                OutlineEntity.entity_type == 'Page'
            ).all()
        }

    @staticmethod
    def default_outline_file_path(topic: Topic):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
        output_path = f"{output_directory}/{topic.slug}"
        default_file_path = f"{output_path}/master-outline.yaml"

        return default_file_path

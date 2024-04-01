import os
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, JSON, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import Session, mapped_column, relationship
from sqlalchemy.orm.attributes import flag_modified
from termcolor import colored
from src.utils.strings import slugify, string_hash
from .base import Base


class Page(Base):
    __tablename__ = "page"
    id = mapped_column(Integer, primary_key=True)
    topic_id = mapped_column(ForeignKey("topic.id"))
    course_id = mapped_column(Integer, nullable=False, index=True)
    chapter_id = mapped_column(Integer, nullable=False, index=True)
    name = mapped_column(String, nullable=False)
    slug = mapped_column(String, nullable=False)
    permalink = mapped_column(String)
    link = mapped_column(String)
    path = mapped_column(String)
    hash = mapped_column(String, unique=True)
    type = mapped_column(String)
    content = mapped_column(Text)
    summary = mapped_column(Text)
    position = mapped_column(Integer, nullable=False)
    position_in_course = mapped_column(Integer, nullable=False)
    generated = mapped_column(Boolean, default=False)
    properties = mapped_column(JSON)
    active = mapped_column(Boolean, default=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    topic = relationship("Topic", back_populates="pages")


    def get_properties(self):
        return self.properties or {}


    def update_properties(self, db: Session, properties: dict):
        self.properties = self.get_properties()
        self.properties.update(properties)
        flag_modified(self, 'properties')
        db.commit()

        return self


    def dump_page(self):
        print(colored(f"Writing page: {self.path}", "green"))

        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'w', encoding="utf-8") as f:
            f.write(self.content)
            f.close()


    def to_dict(self):
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "course_id": self.course_id,
            "chapter_id": self.chapter_id,
            "name": self.name,
            "slug": self.slug,
            "permalink": self.permalink,
            "link": self.link,
            "path": self.path,
            "hash": self.hash,
            "type": self.type,
            "content": self.content,
            "summary": self.summary,
            "position": self.position,
            "position_in_course": self.position_in_course,
            "generated": self.generated,
            "properties": self.properties,
            "active": self.active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def make_slug(cls, name, course_slug, chapter_slug):
        if name == 'Practice Skill Challenge':
            return f"challenge-{chapter_slug}"
        if 'Final Skill Challenge' in name:
            return f"{course_slug}-{slugify(name)}"
        return slugify(name)


    @classmethod
    def hash_page(cls, content):
        page_material = content.strip()

        try:
            return string_hash(page_material)
        except Exception:
            return None


    @classmethod
    def get_page_type(cls, name, chapter_slug):
        if "final-skill-challenge" in chapter_slug:
            return 'final-skill-challenge'

        if 'Practice Skill Challenge' in name:
            return 'challenge'

        return 'lesson'


    @staticmethod
    def dump_pages(pages: list):
        for page in pages:
            page.dump_page()

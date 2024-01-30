import os
from .base import Base
from .topic import Topic
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, JSON, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, relationship
from src.utils.strings import slugify, string_hash
from sqlalchemy.orm import Session



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

    topic = relationship("Topic", back_populates="pages")

    def make_slug(name, course_slug, chapter_slug):
        if name == 'Practice Skill Challenge':
            return f"challenge-{chapter_slug}"
        if 'Final Skill Challenge' in name:
            return f"{course_slug}-{slugify(name)}"
        return slugify(name)


    def hash_page(content):
        page_material = content.strip()

        try:
            return string_hash(page_material)
        except Exception:
            return None


    def get_page_type(name, chapter_slug):
        if "final-skill-challenge" in chapter_slug:
            return 'final-skill-challenge'

        if ('Challenge' in name):
            return 'challenge'

        return 'page'

    def to_dict(self):
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "course_slug": self.course_slug,
            "chapter_slug": self.chapter_slug,
            "name": self.name,
            "slug": self.slug,
            "permalink": self.permalink,
            "link": self.link,
            "path": self.path,
            "hash": self.hash,
            "type": self.type,
            "content": self.content,
            "summary": self.summary,
            "nodes": self.nodes,
            "position": self.position,
            "position_in_course": self.position_in_course,
            "position_in_series": self.position_in_series,
            "generated": self.generated,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


    @classmethod
    def first_or_create(self, session: Session, data: dict):
        topic = session.get(Topic, data['topicId'])

        name = data['name']
        course_slug = data['courseSlug']
        chapter_slug = data['chapterSlug']
        outline_name = data['outlineName']
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'

        page_slug = self.make_slug(name, course_slug, chapter_slug)

        page = session.query(self).filter(
            Page.topic_id == topic.id,
            Page.course_slug == course_slug,
            Page.chapter_slug == chapter_slug,
            Page.slug == page_slug
        ).first()

        if not page:
            page = Page(topic_id=topic.id)

        page.name = name
        page.course_slug = course_slug
        page.chapter_slug = chapter_slug
        page.slug = page_slug
        page.path = f"{output_directory}/{topic.slug}/{outline_name}/content/{course_slug}/{chapter_slug}/page-{page_slug}.md"
        page.generated = os.path.exists(page.path)
        page.content = open(page.path).read() if page.generated else None
        page.hash = self.hash_page(page.content) if page.generated else None
        page.permalink = f"/page/{topic.slug}/{course_slug}/{chapter_slug}/{page_slug}"
        page.link = page.permalink if page.generated else '#'
        page.position = data['position']
        page.position_in_course = data['positionInCourse']
        page.position_in_series = data['positionInSeries']
        page.type = self.get_page_type()

        return page

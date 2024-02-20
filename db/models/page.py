import os
from .base import Base
from .topic import Topic
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, JSON, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, relationship
from src.utils.strings import slugify, string_hash
from termcolor import colored
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


    def dump_page(self):
        print(colored(f"Writing page: {self.path}", "green"))

        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'w') as f:
            f.write(self.content)
            f.close()


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
            "generated": self.generated,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


    @classmethod
    def first_or_create(self, session: Session, topic: Topic, data: dict):
        name = data['name']
        course_slug = data['courseSlug']
        chapter_slug = data['chapterSlug']
        outline_name = data['outlineName']
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'

        page_slug = self.make_slug(name, course_slug, chapter_slug)

        page = session.query(self).filter(
            self.topic_id == topic.id,
            self.course_slug == course_slug,
            self.chapter_slug == chapter_slug,
            self.slug == page_slug
        ).first()

        if not page:
            page = self(topic_id=topic.id)

        def get_page_content():
            if page.content: return page.content
            if os.path.exists(page.path): return open(page.path).read()
            return data.get('content', None)

        page.name = name
        page.course_slug = course_slug
        page.chapter_slug = chapter_slug
        page.slug = page_slug
        page.path = f"{output_directory}/{topic.slug}/{outline_name}/content/{course_slug}/{chapter_slug}/page-{page_slug}.md"
        page.content = get_page_content()
        page.summary = page.summary or data.get('summary', None)
        page.nodes = page.nodes or data.get('nodes', None)
        page.generated = os.path.exists(page.path) or page.content != None
        page.hash = self.hash_page(page.content) if page.content else None
        page.permalink = f"/page/{topic.slug}/{course_slug}/{chapter_slug}/{page_slug}"
        page.link = page.permalink if page.generated else '#'
        page.position = data['position']
        page.position_in_course = data['positionInCourse']
        page.type = self.get_page_type(name, chapter_slug)

        return page


    @classmethod
    def handle_existing_page_material(self, session: Session, page):
        material = open(page.path, 'r').read()
        hash = self.hash_page(material)

        if page.hash != hash:
            page.content = material
            page.generated = True
            page.link = page.permalink
            page.hash = hash

            session.commit()

            return True
        return False


    @classmethod
    def check_for_existing_page_material(self, session: Session, page) -> bool:
        existing_content = page.content != None
        file_exists = os.path.exists(page.path)

        if file_exists and not existing_content:
            return self.handle_existing_page_material(session, page)

        return existing_content


    @staticmethod
    def dump_pages(pages: list):
        for page in pages:
            page.dump_page()

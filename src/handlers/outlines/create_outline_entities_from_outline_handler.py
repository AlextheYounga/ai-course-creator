from db.db import DB, Outline, OutlineEntity, Course, Chapter, Page
from src.events.event_manager import EVENT_MANAGER
from src.events.events import OutlineEntitiesCreatedFromOutline
import os


class CreateOutlineEntitiesFromOutlineHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.topic = self.outline.topic

    def handle(self) -> list[Page]:
        master_outline = self.outline.master_outline

        for course_index, course in enumerate(master_outline):
            page_position_in_course = 0
            course = course['course']

            # Building course record
            course_record = self._get_first_or_create_course(course['courseName'], course_index)
            DB.add(course_record)

            for chapter_index, chapter in enumerate(course['chapters']):
                # Building chapter record
                chapter_record = self._get_first_or_create_chapter(chapter['name'], chapter_index, course_record)
                DB.add(chapter_record)

                # Building page record
                for page_index, page in enumerate(chapter['pages']):
                    page_record = self._get_first_or_create_page(
                        page,
                        page_index,
                        page_position_in_course,
                        chapter_record,
                        course_record
                    )

                    DB.add(page_record)
                    page_position_in_course += 1

                    # Saving to the database
                    DB.commit()

                    # Create outline entities
                    OutlineEntity.first_or_create(DB, self.outline.id, page_record)
                OutlineEntity.first_or_create(DB, self.outline.id, chapter_record)
            OutlineEntity.first_or_create(DB, self.outline.id, course_record)

        return self.__trigger_completion_event({
            'threadId': self.thread_id,
            'outlineId': self.outline.id,
            'topicId': self.topic.id,
        })


    def _get_first_or_create_course(self, name, position):
        course_slug = Course.make_slug(name)

        course = DB.query(Course).filter(
            Course.topic_id == self.topic.id,
            Course.slug == course_slug
        ).first()

        if not course:
            course = Course(topic_id=self.topic.id)

        course.name = name
        course.slug = course_slug
        course.level = position
        course.skill_challenge_chapter = f"final-skill-challenge-{course_slug}"

        return course


    def _get_first_or_create_chapter(self, name, position, course: Course):
        chapter_slug = Chapter.make_slug(name, course.slug)

        chapter = DB.query(Chapter).filter(
            Chapter.topic_id == self.topic.id,
            Chapter.slug == chapter_slug
        ).first()

        if not chapter:
            chapter = Chapter(topic_id=self.topic.id, course_id=course.id)

        chapter.name = name
        chapter.slug = chapter_slug
        chapter.position = position
        chapter.content_type = Chapter.get_content_type(chapter_slug)

        return chapter


    def _get_first_or_create_page(self, name: str, position: int, position_in_course: int, chapter: Chapter, course: Course):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'

        page_slug = Page.make_slug(name, course.slug, chapter.slug)

        page = DB.query(Page).filter(
            Page.topic_id == self.topic.id,
            Page.course_id == course.id,
            Page.chapter_id == chapter.id,
            Page.slug == page_slug
        ).first()

        if not page:
            page = Page(topic_id=self.topic.id)

        def get_page_content():
            if page.content: return page.content
            if os.path.exists(page.path): return open(page.path).read()
            return None

        page.name = name
        page.course_id = course.id
        page.chapter_id = chapter.id
        page.slug = page_slug
        page.path = f"{output_directory}/{self.topic.slug}/{self.outline.name}/content/{course.slug}/{chapter.slug}/page-{page_slug}.md"
        page.content = get_page_content()
        page.summary = page.summary
        page.nodes = page.nodes
        page.generated = os.path.exists(page.path) or page.content != None
        page.hash = Page.hash_page(page.content) if page.content else None
        page.permalink = f"/page/{self.topic.slug}/{course.slug}/{chapter.slug}/{page_slug}"
        page.link = page.permalink if page.generated else '#'
        page.position = position
        page.position_in_course = position_in_course
        page.type = Page.get_page_type(name, chapter.slug)

        return page


    def __trigger_completion_event(self, data: dict):
        EVENT_MANAGER.trigger(OutlineEntitiesCreatedFromOutline(data))
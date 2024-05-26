import os
from db.db import DB, Outline, OutlineEntity, Course, Chapter, Page
from src.events.events import OutlineEntitiesCreatedFromOutline, GenerateOutlineJobFinished



class CreateOutlineEntitiesFromOutlineHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.outline = self.db.get(Outline, data['outlineId'])
        self.topic = self.outline.topic

    def handle(self):
        outline_data = self.outline.outline_data

        for course_index, course in enumerate(outline_data):
            page_position_in_course = 0
            course = course['course']

            # Building course record
            course_record = self._get_first_or_create_course(course['courseName'], course_index)

            for chapter_index, chapter in enumerate(course['chapters']):
                # Building chapter record
                chapter_record = self._get_first_or_create_chapter(chapter['name'], chapter_index, course_record)

                # Building page record
                for page_index, page in enumerate(chapter['pages']):
                    page_record = self._get_first_or_create_page(
                        page,
                        page_index,
                        page_position_in_course,
                        chapter_record,
                        course_record
                    )

                    page_position_in_course += 1

                    # Saving to the database
                    self.db.commit()

                    # Create outline entities
                    OutlineEntity.first_or_create(self.db, self.outline.id, page_record)
                OutlineEntity.first_or_create(self.db, self.outline.id, chapter_record)
            OutlineEntity.first_or_create(self.db, self.outline.id, course_record)

        return [
            OutlineEntitiesCreatedFromOutline(self.data),
            GenerateOutlineJobFinished(self.data)
        ]


    def _get_first_or_create_course(self, name, position):
        course_slug = Course.make_slug(name)

        course = self.db.query(Course).filter(
            Course.topic_id == self.topic.id,
            Course.slug == course_slug
        ).first()

        if not course:
            course = Course(topic_id=self.topic.id)

        properties = {
            'skillChallengeChapter': f"final-skill-challenge-{course_slug}"
        }

        course.name = name
        course.slug = course_slug
        course.level = position
        course.properties = properties

        self.db.add(course)

        return course


    def _get_first_or_create_chapter(self, name, position, course: Course):
        chapter_slug = Chapter.make_slug(name, course.slug)

        chapter = self.db.query(Chapter).filter(
            Chapter.topic_id == self.topic.id,
            Chapter.slug == chapter_slug
        ).first()

        if not chapter:
            chapter = Chapter(topic_id=self.topic.id, course_id=course.id)

        chapter.name = name
        chapter.slug = chapter_slug
        chapter.position = position
        chapter.content_type = Chapter.get_content_type(chapter_slug)

        self.db.add(chapter)

        return chapter


    def _get_first_or_create_page(self, name: str, position: int, position_in_course: int, chapter: Chapter, course: Course):
        page_slug = Page.make_slug(name, course.slug, chapter.slug)

        page = self.db.query(Page).filter(
            Page.topic_id == self.topic.id,
            Page.course_id == course.id,
            Page.chapter_id == chapter.id,
            Page.slug == page_slug
        ).first()

        if not page:
            page = Page(topic_id=self.topic.id)

        page.name = name
        page.course_id = course.id
        page.chapter_id = chapter.id
        page.slug = page_slug
        page.content = page.content if page.content else None
        page.summary = page.summary
        page.generated = page.content != None
        page.hash = Page.hash_page(page.content) if page.content else None
        page.link = f"/page/{self.topic.slug}/{course.slug}/{chapter.slug}/{page_slug}"
        page.position = position
        page.position_in_course = position_in_course
        page.type = Page.get_page_type(name, chapter.slug)

        self.db.add(page)

        return page

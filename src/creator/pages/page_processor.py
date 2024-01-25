import os
from db.db import db_client, Page
from src.utils.strings import string_hash


DB = db_client()


class PageProcessor:
    @staticmethod
    def hash_page(content):
        page_material = content.strip()

        try:
            return string_hash(page_material)
        except Exception:
            return None


    @staticmethod
    def handle_existing_page_material(file_exists: bool, row: dict, page_record: Page | None):
        if file_exists and not page_record:
            page_record = PageProcessor.create_page_record_from_file(row)
        if page_record:
            PageProcessor.update_existing_record_from_outline(page_record, row)


    @staticmethod
    def check_for_existing_page_material(topic_id: int, row: dict) -> bool:
        page_slug = row['slug']
        file_exists = os.path.exists(row['path'])

        page_record = DB.query(Page).filter(
            Page.topic_id == topic_id,
            Page.course_slug == row['courseSlug'],
            Page.chapter_slug == row['chapterSlug'],
            Page.slug == page_slug
        ).first()

        if file_exists or page_record:
            PageProcessor.handle_existing_page_material(file_exists, row, page_record)
            return True

        return False


    @staticmethod
    def update_existing_record_from_outline(page: Page, data: dict):
        page.name = data['name']
        page.course_slug = data['courseSlug']
        page.chapter_slug = data['chapterSlug']
        page.slug = data['slug']
        page.permalink = data['permalink']
        page.link = data['link']
        page.course_data = data['courseData']
        page.position = data['position']
        page.position_in_series = data['positionInSeries']
        page.position_in_course = data['positionInCourse']

        DB.add(page)
        DB.commit()

        return page


    @staticmethod
    def create_page_record_from_file(topic_id: int, row: dict):
        material = open(row['path'], 'r').read()
        hash = PageProcessor.hash_page(material)

        existing_record = DB.get(Page).filter(Page.hash == hash).first()
        if existing_record:
            return PageProcessor.update_existing_record_from_row(existing_record, row)

        page_record = Page(
            topic_id=topic_id,
            name=row['name'],
            course_slug=row['courseSlug'],
            chapter_slug=row['chapterSlug'],
            slug=row['slug'],
            permalink=row['permalink'],
            link=row['link'],
            hash=hash,
            content=material,
            course_data=row['courseData'],
            position=row['position'],
            position_in_series=row['positionInSeries'],
            position_in_course=row['positionInCourse'],
            generated=True,
        )

        DB.add(page_record)
        DB.commit()

        return page_record

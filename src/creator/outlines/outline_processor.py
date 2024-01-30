import os
from termcolor import colored
from dotenv import load_dotenv
from db.db import DB, Topic, Outline, Course, Chapter, Page
from src.utils.files import read_yaml_file
from src.utils.strings import string_hash
from src.creator.pages.page_processor import PageProcessor
import yaml


load_dotenv()


class OutlineProcessor:
    def __init__(self, outline_id: int):
        self.outline_id = outline_id
        self.outline = DB.get(Outline, self.outline_id)
        self.topic = self.outline.topic
        self.output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'


    # Private Methods


    def _create_or_update_course_record_from_outline(self, data):
        course_slug = Course.make_slug(data['name'])

        course = DB.query(Course).filter(
            Course.topic_id == self.topic.id,
            Course.slug == course_slug
        ).first()

        if not course:
            course = Course(topic_id=self.topic.id)

        course.name = data['name']
        course.slug = course_slug
        course.level = data['position']
        course.outline = data['outline']
        course.skill_challenge_chapter = f"final-skill-challenge-{course_slug}"

        return course


    def _create_or_update_chapter_record_from_outline(self, data):
        chapter_slug = Chapter.make_slug(data['name'], data['courseSlug'])

        chapter = DB.query(Chapter).filter(
            Chapter.topic_id == self.topic.id,
            Chapter.slug == chapter_slug
        ).first()

        if not chapter:
            chapter = Chapter(topic_id=self.topic.id)

        chapter.name = data['name']
        chapter.slug = chapter_slug
        chapter.course_slug = data['courseSlug']
        chapter.position = data['position']
        chapter.outline = data['outline']
        chapter.content_type = 'lesson' if data['name'] != 'Final Skill Challenge' else 'final-skill-challenge'

        return chapter


    def _create_or_update_page_record_from_outline(self, data):
        course_slug = data['courseSlug']
        chapter_slug = data['chapterSlug']

        page_slug = Page.make_slug(data['name'], course_slug, chapter_slug)

        page = DB.query(Page).filter(
            Page.topic_id == self.topic.id,
            Page.course_slug == course_slug,
            Page.chapter_slug == chapter_slug,
            Page.slug == page_slug
        ).first()

        if not page:
            page = Page(topic_id=self.topic.id)

        page.name = data['name']
        page.course_slug = course_slug
        page.chapter_slug = chapter_slug
        page.slug = page_slug
        page.path = f"{self.output_directory}/{self.topic.slug}/{self.outline.name}/content/{course_slug}/{chapter_slug}/page-{page_slug}.md"
        page.generated = os.path.exists(page.path)
        page.content = open(page.path).read() if page.generated else None
        page.hash = PageProcessor.hash_page(page.content) if page.generated else None
        page.permalink = f"/page/{self.topic.slug}/{course_slug}/{chapter_slug}/{page_slug}"
        page.link = page.permalink if page.generated else '#'
        page.position = data['position']
        page.position_in_course = data['positionInCourse']
        page.position_in_series = data['positionInSeries']
        page.type = Page.get_page_type(page.name, chapter_slug)

        return page


    def _find_or_create_records_from_outline(self):
        pages = []
        for course_index, course in enumerate(self.outline.master_outline):
            page_position_in_course = 0
            course = course['course']

            # Building course record
            course_record = self._create_or_update_course_record_from_outline({
                'name': course['courseName'],
                'position': course_index,
                'outline': yaml.dump(course, sort_keys=False),
            })
            DB.add(course_record)

            for chapter_index, chapter in enumerate(course['chapters']):
                # Building chapter record
                chapter_name = chapter['name']

                chapter_record = self._create_or_update_chapter_record_from_outline({
                    'name': chapter_name,
                    'courseSlug': course_record.slug,
                    'position': chapter_index,
                    'outline': yaml.dump(chapter, sort_keys=False),
                })

                DB.add(chapter_record)

                # Building page record
                for page_index, page in enumerate(chapter['pages']):
                    page_record = self._create_or_update_page_record_from_outline({
                        'name': page,
                        'courseSlug': course_record.slug,
                        'chapterSlug': chapter_record.slug,
                        'position': page_index,
                        'positionInCourse': page_position_in_course,
                        'positionInSeries': len(pages),
                    })
                    page_position_in_course += 1

                    # Saving to the database
                    DB.add(page_record)
                    DB.commit()
                    DB.refresh(page_record)

                    pages.append(page_record)

        return pages


    def _get_record_ids_from_outline(self):
        records = {
            'courses': [],
            'chapters': [],
            'pages': []
        }

        for course in self.outline.master_outline:
            course = course['course']
            course_slug = Course.make_slug(course['courseName'])
            course_record = DB.query(Course).filter(Course.topic_id == self.topic.id, Course.slug == course_slug).first()
            records['courses'].append(course_record.id)

            for chapter in course['chapters']:
                chapter_slug = Chapter.make_slug(chapter['name'], course_slug)
                chapter_record = DB.query(Chapter).filter(Chapter.topic_id == self.topic.id, Chapter.slug == chapter_slug).first()
                records['chapters'].append(chapter_record.id)

                for page in chapter['pages']:
                    page_slug = Page.make_slug(page, course_slug, chapter_slug)
                    page_record = DB.query(Page).filter(Page.topic_id == self.topic.id, Page.slug == page_slug).first()
                    records['pages'].append(page_record.id)

        return records


    # Static Methods


    @staticmethod
    def instantiate_new_outline(topic_id: int) -> Outline:
        existing_outline_count = DB.query(Outline).filter(Outline.topic_id == topic_id).count()
        next_outline_number = str(existing_outline_count + 1)
        outline_name = f"series-{next_outline_number}"

        new_outline = Outline(
            topic_id=topic_id,
            name=outline_name
        )

        return new_outline


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
    def get_or_create_outline_record_from_file(topic_id: int, outline_file: str):
        outline = OutlineProcessor.get_outline_record_from_file(outline_file)
        if outline: return outline

        print(colored("Detected new outline. Processing...\n", "yellow"))
        new_outline = OutlineProcessor.create_new_outline_from_file(topic_id, outline_file)
        print(colored(f"New outline created {new_outline.name}\n", "green"))

        return new_outline


    @staticmethod
    def create_new_outline_from_file(topic_id: int, outline_file: str):
        # Create new outline record
        topic = DB.get(Topic, topic_id)

        last_outline = DB.query(Outline).filter(
            Outline.topic_id == topic_id
        ).order_by(
            Outline.id.desc()
        ).first()

        new_outline = OutlineProcessor.instantiate_new_outline(topic.id)
        new_outline.master_outline = read_yaml_file(outline_file)  # Add changed outline to record
        new_outline.hash = OutlineProcessor.hash_outline(new_outline.master_outline)

        if last_outline:
            new_outline.skills = last_outline.skills

        DB.add(new_outline)
        DB.commit()

        return new_outline


    @staticmethod
    def dump_pages_from_outline(outline_id: int):
        processor = OutlineProcessor(outline_id)

        outline_record_ids = processor._get_record_ids_from_outline()
        page_ids = outline_record_ids['pages']

        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
        output_path = f"{output_directory}/{processor.topic.slug}"

        page_records = DB.query(Page).filter(Page.id.in_(page_ids)).all()

        for page in page_records:
            if not page.content: continue
            # Write to file
            PageProcessor.dump_page(page)


        with open(f"{output_path}/{processor.outline.name}/skills.yaml", 'w') as skills_file:
            skills_file.write(yaml.dump(processor.outline.skills, sort_keys=False))
            skills_file.close()

        with open(f"{output_path}/{processor.outline.name}/outline.yaml", 'w') as outline_file:
            outline_file.write(yaml.dump(processor.outline.master_outline, sort_keys=False))
            outline_file.close()


    @staticmethod
    def get_outline_record_from_file(outline_file: str):
        outline_data = open(outline_file).read()
        outline_hash = OutlineProcessor.hash_outline(outline_data)
        outline = DB.query(Outline).filter(Outline.hash == outline_hash).first()

        if outline:
            return outline
        return None


    @staticmethod
    def get_outline_record_ids(outline_id: int):
        processor = OutlineProcessor(outline_id)
        return processor._get_record_ids_from_outline()


    @staticmethod
    def get_outline_records(outline_id: int):
        processor = OutlineProcessor(outline_id)
        return processor._find_or_create_records_from_outline()

import os
from db.db import DB, Topic, Outline, OutlineEntity, Course, Chapter, Page
from openai import OpenAI
from src.creator.outlines.outline_creator import OutlineCreator
from src.creator.challenges.practice_skill_challenge_creator import PracticeSkillChallengeCreator
from src.creator.challenges.final_skill_challenge_creator import FinalSkillChallengeCreator
from src.creator.pages.page_material_creator import PageMaterialCreator
import progressbar


class CourseCreator:
    def __init__(self, client: OpenAI, topic_name: str):
        self.topic = Topic.first_or_create(DB, name=topic_name)
        self.client = client
        self.pages = []


    def create_outline(self):
        session_name = f"Topic Outline Generation - {self.topic.name}"
        creator = OutlineCreator(self.topic.id, self.client(session_name))
        outline_id = creator.create()

        return outline_id


    def create_topic_page_material(self):
        session_name = f"Topic Page Generation - {self.topic.name}"

        creator = PageMaterialCreator(self.topic.id, self.client(session_name))
        pages = creator.create_from_outline()

        return pages


    def create_topic_practice_skill_challenges(self):
        session_name = f"Topic Challenge Generation - {self.topic.name}"

        creator = PracticeSkillChallengeCreator(self.topic.id, self.client(session_name))
        pages = creator.create_from_outline()

        return pages


    def create_topic_final_skill_challenges(self):
        session_name = f"Topic Final Skill Challenge Generation - {self.topic.name}"

        creator = FinalSkillChallengeCreator(self.topic.id, self.client(session_name))
        pages = creator.create_from_outline()

        return pages


    def generate_topic_courses(self):
        self.create_outline()
        self.create_topic_page_material()
        self.create_topic_practice_skill_challenges()
        self.create_topic_final_skill_challenges()


    def generate_course(self, course: Course):
        outline = Outline.get_or_create_from_file(DB, self.topic.id)
        session_name = f"Course Generation - {course.name}"

        page_creator = PageMaterialCreator(self.topic.id, self.client(session_name))
        challenge_creator = PracticeSkillChallengeCreator(self.topic.id, self.client(session_name))
        fsc_creator = FinalSkillChallengeCreator(self.topic.id, self.client(session_name))

        pages = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == outline.id,
            OutlineEntity.entity_type == 'Page',
            Page.course_slug == course.slug
        ).all()

        generated_pages = []

        for page in pages:
            if page.type == 'page':
                page = page_creator.generate_page_material(page)
                generated_pages.append(page)
            if page.type == 'challenge':
                page = challenge_creator.generate_practice_skill_challenge(page)
                generated_pages.append(page)

        fsc_creator.generate_final_skill_challenge(course)


    def generate_chapter(self, chapter: Chapter):
        outline = Outline.get_or_create_from_file(DB, self.topic.id)
        session_name = f"Chapter Generation - {chapter.name}"

        page_creator = PageMaterialCreator(self.topic.id, self.client(session_name))
        challenge_creator = PracticeSkillChallengeCreator(self.topic.id, self.client(session_name))

        pages = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == outline.id,
            OutlineEntity.entity_type == 'Page',
            Page.course_slug == chapter.course_slug,
            Page.chapter_slug == chapter.slug
        ).all()

        generated_pages = []

        for page in pages:
            if page.type == 'page':
                page = page_creator.generate_page_material(page)
                generated_pages.append(page)
            if page.type == 'challenge':
                page = challenge_creator.generate_practice_skill_challenge(page)
                generated_pages.append(page)

        return generated_pages


    def generate_chapter_challenge(self, chapter: Chapter):
        outline = Outline.get_or_create_from_file(DB, self.topic.id)
        session_name = f"Chapter Generation - {chapter.name}"

        challenge_creator = PracticeSkillChallengeCreator(self.topic.id, self.client(session_name))

        pages = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == outline.id,
            OutlineEntity.entity_type == 'Page',
            Page.course_slug == chapter.course_slug,
            Page.chapter_slug == chapter.slug,
            Page.type == 'challenge'
        ).all()

        generated_pages = []

        for page in pages:
            page = challenge_creator.generate_practice_skill_challenge(page)
            generated_pages.append(page)

        return generated_pages



    def generate_course_challenges(self, course: Course):
        outline = Outline.get_or_create_from_file(DB, self.topic.id)

        pages = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == outline.id,
            OutlineEntity.entity_type == 'Page',
            Page.type == 'challenge',
            Page.course_slug == course.slug
        ).all()

        session_name = f"Course Practice Challenge Generation - {self.topic.name}"
        creator = PracticeSkillChallengeCreator(self.topic.id, self.client(session_name))
        generated_pages = []
        for page in pages:
            generated_page = creator.generate_practice_skill_challenge(page)
            generated_pages.append(generated_page)

        return generated_pages


    def generate_course_final_skill_challenge(self, course: Course):
        session_name = f"Course Final Skill Challenge Generation - {self.topic.name}"

        creator = FinalSkillChallengeCreator(self.topic.id, self.client(session_name))
        pages = creator.generate_final_skill_challenge(course)

        return pages


    def generate_entity_page_material(self, record: Course | Chapter | Page):
        outline = Outline.get_or_create_from_file(DB, self.topic.id)
        page_entities = Outline.get_entities_by_type(DB, outline.id, 'Page')
        record_type = type(record).__name__

        page_creator = PageMaterialCreator(
            self.topic.id,
            self.client(f"Page Generation - {record.name}")
        )

        pages_to_generate = []
        generated_pages = []

        # Generate all pages for course
        if record_type == 'Page' and record.type == 'page':
            if Page.check_for_existing_page_material(page): return
            return page_creator.generate_page_material(page)

        elif record_type == 'Course':
            pages_to_generate = [
                page for page in page_entities
                if page.course_slug == record.slug and page.type == 'page'
            ]

        elif record_type == 'Chapter':
            pages_to_generate = [
                page for page in page_entities
                if page.course_slug == record.slug and page.slug == record.slug and page.type == 'page'
            ]

        with progressbar.ProgressBar(max_value=len(pages_to_generate), prefix='Generating pages: ', redirect_stdout=True) as bar:
            for page in pages_to_generate:
                bar.increment()
                if Page.check_for_existing_page_material(page): continue
                page = page_creator.generate_page_material(page)
                generated_pages.append(page)

        return generated_pages


    def generate_page_material(self, page: Page):
        page_creator = PageMaterialCreator(self.topic.id, self.client(f"Page Generation - {page.name}"))
        challenge_creator = PracticeSkillChallengeCreator(self.topic.id, self.client(f"Skill Challenge Generation - {page.name}"))

        creators = {
            'page': page_creator.generate_page_material,
            'challenge': challenge_creator.generate_practice_skill_challenge
        }
        if Page.check_for_existing_page_material(page): return
        return creators[page.type](page)

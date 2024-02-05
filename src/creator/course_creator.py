import os
from db.db import DB, Topic, Outline, Course, Chapter, Page
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


    def generate_course_final_skill_challenge(self, course: Course):
        session_name = f"Course Final Skill Challenge Generation - {self.topic.name}"

        creator = FinalSkillChallengeCreator(self.topic.id, self.client(session_name))
        pages = creator.generate_final_skill_challenge(course)

        return pages


    def generate_course_material(self, course: Course):
        session_name = f"Course Generation - {course.name}"

        page_creator = PageMaterialCreator(self.topic.id, self.client(session_name))
        challenge_creator = PracticeSkillChallengeCreator(self.topic.id, self.client(session_name))
        fsc_creator = FinalSkillChallengeCreator(self.topic.id, self.client(session_name))

        pages = DB.query(Page).filter(
            Page.topic_id == self.topic.id,
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


    def generate_chapter_material(self, chapter: Chapter):
        session_name = f"Chapter Generation - {chapter.name}"

        page_creator = PageMaterialCreator(self.topic.id, self.client(session_name))
        challenge_creator = PracticeSkillChallengeCreator(self.topic.id, self.client(session_name))

        pages = DB.query(Page).filter(
            Page.topic_id == self.topic.id,
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


    def dynamic_generate_page_material(self, content_type: str, record: Course | Chapter | Page):
        outline = self.topic.get_latest_outline()
        page_entities = Outline.get_entities_by_type(DB, outline.id, 'Page')

        creator_function_call = None
        if content_type == 'challenge':
            session_name = f"{type(record).__name__} Skill Challenge Generation - {record.name}"
            creator = PageMaterialCreator(self.topic.id, self.client(session_name))
            creator_function_call = creator.generate_page_material
        else:
            session_name = f"{type(record).__name__} Page Generation - {record.name}"
            creator = PracticeSkillChallengeCreator(self.topic.id, self.client(session_name))
            creator_function_call = creator.generate_practice_skill_challenge

        generated_pages = []

        # Generate all pages for course
        if isinstance(record, Course):
            course_pages = [
                page for page in page_entities
                if page.course_slug == record.slug and page.type == content_type
            ]

            with progressbar.ProgressBar(max_value=len(course_pages), prefix='Generating: ', redirect_stdout=True) as bar:
                for page in course_pages:
                    bar.increment()
                    if Page.check_for_existing_page_material(page): continue
                    page = creator_function_call(page)
                    generated_pages.append(page)

        # Generate all pages for chapter
        elif isinstance(record, Chapter):
            chapter_pages = [
                page for page in page_entities
                if page.course_slug == record.slug and page.slug == record.slug and page.type == content_type
            ]

            with progressbar.ProgressBar(max_value=len(chapter_pages), prefix='Generating: ', redirect_stdout=True) as bar:
                for page in chapter_pages:
                    bar.increment()
                    if Page.check_for_existing_page_material(page): continue
                    page = creator_function_call(page)
                    generated_pages.append(page)

        # Generate page
        elif isinstance(record, Page):
            if page.type == content_type:
                if Page.check_for_existing_page_material(page): return
                return creator_function_call(page)

        return generated_pages

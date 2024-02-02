import os
from db.db import DB, Topic, Outline, Course, Chapter, Page
from openai import OpenAI
from src.llm.openai_handler import OpenAiHandler
from src.creator.outlines.outline_creator import OutlineCreator
from src.creator.challenges.practice_skill_challenge_creator import PracticeSkillChallengeCreator
from src.creator.challenges.final_skill_challenge_creator import FinalSkillChallengeCreator
from src.creator.pages.page_material_creator import PageMaterialCreator
import yaml


class CourseCreator:
    def __init__(self, topic_name: str, client: OpenAI):
        self.topic = Topic.first_or_create(DB, name=topic_name)
        self.ai_handler = client
        self.pages = []


    def create_outline(self):
        creator = OutlineCreator(self.topic.id, self.ai_handler)
        outline_id = creator.create()

        return outline_id


    def create_topic_page_material(self):
        creator = PageMaterialCreator(self.topic.id, self.ai_handler)
        pages = creator.create_from_outline()

        return pages



    def create_topic_practice_skill_challenges(self):
        creator = PracticeSkillChallengeCreator(self.topic.id, self.ai_handler)
        pages = creator.create_from_outline()

        return pages


    def create_topic_final_skill_challenges(self):
        creator = FinalSkillChallengeCreator(self.topic.id, self.ai_handler)
        pages = creator.create_from_outline()

        return pages


    def generate_topic_courses(self):
        CourseCreator.create_outline()
        CourseCreator.create_page_material()
        CourseCreator.create_practice_skill_challenges()
        CourseCreator.create_final_skill_challenges()


    def generate_course_material(self, course: Course):
        ai_client = OpenAiHandler(f"Course Generation - {course.name}")

        page_creator = PageMaterialCreator(self.topic.id, ai_client)
        challenge_creator = PracticeSkillChallengeCreator(self.topic.id, ai_client)
        fsc_creator = FinalSkillChallengeCreator(self.topic.id, ai_client)

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
        ai_client = OpenAiHandler(f"Chapter Generation - {chapter.name}")

        page_creator = PageMaterialCreator(self.topic.id, ai_client)
        challenge_creator = PracticeSkillChallengeCreator(self.topic.id, ai_client)

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


    def generate_page_material(self, page: Page):
        ai_client = OpenAiHandler(f"{page.name} Page Generation")
        page_creator = PageMaterialCreator(self.topic.id, ai_client)

        if page.type == 'page':
            page = page_creator.generate_page_material(page)

        return page


    @staticmethod
    def dump_outline_content(outline_id: int):
        outline = DB.get(Outline, outline_id)
        topic = outline.topic
        entities = Outline.get_entities()

        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
        output_path = f"{output_directory}/{topic.slug}"

        for page in entities['pages']:
            if not page.content: continue
            # Write to file
            Page.dump_page([page])


        with open(f"{output_path}/{outline.name}/skills.yaml", 'w') as skills_file:
            skills_file.write(yaml.dump(outline.skills, sort_keys=False))
            skills_file.close()

        with open(f"{output_path}/{outline.name}/outline.yaml", 'w') as outline_file:
            outline_file.write(yaml.dump(outline.master_outline, sort_keys=False))
            outline_file.close()

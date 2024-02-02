import os
from db.db import DB, Topic, Outline, Course, Chapter, Page
from src.llm.openai_handler import OpenAiHandler
from src.creator.outlines.outline_creator import OutlineCreator
from src.creator.challenges.practice_skill_challenge_creator import PracticeSkillChallengeCreator
from src.creator.challenges.final_skill_challenge_creator import FinalSkillChallengeCreator
from src.creator.pages.page_material_creator import PageMaterialCreator
import yaml


class CourseCreator:
    @staticmethod
    def run_all(topics: list):
        CourseCreator.create_outlines(topics)
        CourseCreator.create_page_material(topics)
        CourseCreator.create_practice_skill_challenges(topics)
        CourseCreator.create_final_skill_challenges(topics)


    @staticmethod
    def create_outlines(topics: list):
        outline_ids = []
        for topic in topics:
            session_name = f"{topic} Outlines"
            ai_client = OpenAiHandler(session_name)

            creator = OutlineCreator(topic, ai_client)
            outline_id = creator.create()

            outline_ids.append(outline_id)

        return outline_ids


    @staticmethod
    def create_page_material(topics: list):
        outline_ids = []
        for topic in topics:
            session_name = f"{topic} Page Material"
            ai_client = OpenAiHandler(session_name)

            creator = PageMaterialCreator(topic, ai_client)
            outline_id = creator.create_from_outline()

            outline_ids.append(outline_id)

        return outline_ids


    @staticmethod
    def create_practice_skill_challenges(topics: list):
        outline_ids = []
        for topic in topics:
            session_name = f"{topic} Practice Skill Challenges"
            ai_client = OpenAiHandler(session_name)

            creator = PracticeSkillChallengeCreator(topic, ai_client)
            outline_id = creator.create_from_outline()

            outline_ids.append(outline_id)

        return outline_ids


    @staticmethod
    def create_final_skill_challenges(topics: list):
        outline_ids = []
        for topic in topics:
            session_name = f"{topic} Final Skill Challenges"
            ai_client = OpenAiHandler(session_name)

            creator = FinalSkillChallengeCreator(topic, ai_client)
            outline_id = creator.create_from_outline()

            outline_ids.append(outline_id)

        return outline_ids


    @staticmethod
    def generate_specific_pages(topic: Topic, pages: list[Page]):
        ai_client = OpenAiHandler(f"Generate Specific Pages")

        creator = PageMaterialCreator(topic.name, ai_client)
        generated_pages = []

        for page in pages:
            page_generated = creator.generate_page_material(page)
            generated_pages.append(page_generated)

        return generated_pages



    @staticmethod
    def generate_specific_chapter(topic: Topic, chapter: Chapter):
        ai_client = OpenAiHandler(f"Chapter Regeneration")

        # Handle final skill challenge chapter
        if chapter.content_type == 'final-skill-challenge':
            course = DB.query(Course).filter(
                Course.topic_id == topic.id,
                Course.slug == chapter.course_slug
            ).first()

            fsc_creator = FinalSkillChallengeCreator(topic.name, ai_client)
            return fsc_creator.generate_final_skill_challenge(course)

        pages = DB.query(Page).filter(
            Topic.id == topic.id,
            Page.course_slug == chapter.course_slug,
            Page.chapter_slug == chapter.slug
        ).all()

        if len(pages) == 0:
            raise Exception(f"No pages found for course '{chapter.name}'")

        page_creator = PageMaterialCreator(topic.name, ai_client)
        challenge_creator = PracticeSkillChallengeCreator(topic.name, ai_client)

        page_creator.generate_page_material(pages)
        challenge_creator.generate_practice_skill_challenge(pages)


    @staticmethod
    def generate_specific_course(topic: Topic, course: Course):
        topic = DB.query(Topic).filter(Topic.id == course.topic_id).first()
        ai_client = OpenAiHandler(f"Full Course Regeneration")

        pages = DB.query(Page).filter(
            Topic.id == course.topic_id,
            Page.course_slug == course.slug,
        ).all()

        if len(pages) == 0:
            raise Exception(f"No pages found for course '{course.name}'")

        page_creator = PageMaterialCreator(topic.name, ai_client)
        challenge_creator = PracticeSkillChallengeCreator(topic.name, ai_client)
        fsc_creator = FinalSkillChallengeCreator(topic.name, ai_client)

        page_creator.generate_page_material(pages)
        challenge_creator.generate_practice_skill_challenge(pages)
        fsc_creator.generate_final_skill_challenge(course)


    @staticmethod
    def generate_specific_pages(topic: Topic, pages: list[Page]):
        ai_client = OpenAiHandler(f"Specific Page Generation")
        topic = DB.query(Topic).filter(Topic.id == topic.id).first()
        creator = PageMaterialCreator(topic.name, ai_client)

        for page in pages:
            if page.type == 'page':
                creator.generate_page_material(page)



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

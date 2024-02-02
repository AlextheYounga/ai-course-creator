from src.llm.openai_handler import OpenAiHandler
from src.creator.challenges.practice_skill_challenge_creator import PracticeSkillChallengeCreator
from src.creator.challenges.final_skill_challenge_creator import FinalSkillChallengeCreator
from src.creator.pages.page_material_creator import PageMaterialCreator
from db.db import DB, Topic, Course, Chapter, Page


class Regenerator:
    def __init__(self, record: Course | Chapter | Page):
        self.record = record
        self.topic = DB.query(Topic).filter(Topic.id == record.topic_id).first()


    @staticmethod
    def regenerate_course(course: Course):
        topic = DB.query(Topic).filter(Topic.id == course.topic_id).first()
        ai_client = OpenAiHandler(f"Full Course Regeneration")

        pages = DB.query(Page).filter(
            Topic.id == course.topic_id,
            Page.course_slug == course.slug,
        ).all()

        if len(pages) == 0:
            raise Exception(f"No pages found for course '{course.name}'")

        PageMaterialCreator.regenerate(ai_client, topic.name, pages)
        PracticeSkillChallengeCreator.regenerate(ai_client, topic.name, pages)
        FinalSkillChallengeCreator.regenerate(ai_client, topic.name, course)



    @staticmethod
    def regenerate_chapter(chapter: Chapter):
        topic = DB.query(Topic).filter(Topic.id == chapter.topic_id).first()
        ai_client = OpenAiHandler(f"Chapter Regeneration")

        if chapter.content_type == 'final-skill-challenge':
            course = DB.query(Course).filter(
                Course.topic_id == topic.id,
                Course.slug == chapter.course_slug
            ).first()

            return FinalSkillChallengeCreator.regenerate(ai_client, topic.name, course)

        pages = DB.query(Page).filter(
            Topic.id == chapter.topic_id,
            Page.course_slug == chapter.course_slug,
            Page.chapter_slug == chapter.slug
        ).all()

        if len(pages) == 0:
            raise Exception(f"No pages found for course '{chapter.name}'")

        PageMaterialCreator.regenerate(ai_client, topic.name, pages)
        PracticeSkillChallengeCreator.regenerate(ai_client, topic.name, pages)



    @staticmethod
    def regenerate_content(record: Course | Chapter | Page):
        if isinstance(record, Course):
            return Regenerator.regenerate_course()

        elif isinstance(record, Chapter):
            return Regenerator.regenerate_chapter()

        elif isinstance(record, Page):
            ai_client = OpenAiHandler(f"Page Regeneration")
            topic = DB.query(Topic).filter(Topic.id == record.topic_id).first()
            return PageMaterialCreator.regenerate(ai_client, topic.name, [record])

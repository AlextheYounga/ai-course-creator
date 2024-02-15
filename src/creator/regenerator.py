from src.llm.openai_handler import OpenAiHandler
from src.creator.challenges.practice_skill_challenge_creator import PracticeSkillChallengeCreator
from src.creator.challenges.final_skill_challenge_creator import FinalSkillChallengeCreator
from src.creator.pages.page_material_creator import PageMaterialCreator
from db.db import DB, Topic, Outline, Course, Chapter, Page


class Regenerator:
    def __init__(self, topic: Topic):
        self.topic = topic
        self.outline = DB.get(Outline, topic.master_outline_id)


    def regenerate_course(self, course: Course):
        ai_client = OpenAiHandler(f"Full Course Regeneration")

        pages = DB.query(Page).filter(
            Topic.id == course.topic_id,
            Page.course_slug == course.slug,
        ).all()

        if len(pages) == 0:
            raise Exception(f"No pages found for course '{course.name}'")

        PageMaterialCreator.regenerate(ai_client, self.topic, pages)
        PracticeSkillChallengeCreator.regenerate(ai_client, self.topic, pages)
        FinalSkillChallengeCreator.regenerate(ai_client, self.topic, course)



    def regenerate_chapter(self, chapter: Chapter):
        ai_client = OpenAiHandler(f"Chapter Regeneration")

        if chapter.content_type == 'final-skill-challenge':
            course = DB.query(Course).filter(
                Course.topic_id == self.topic.id,
                Course.slug == chapter.course_slug
            ).first()

            return FinalSkillChallengeCreator.regenerate(ai_client, self.topic, course)

        pages = DB.query(Page).filter(
            Topic.id == chapter.topic_id,
            Page.course_slug == chapter.course_slug,
            Page.chapter_slug == chapter.slug
        ).all()

        if len(pages) == 0:
            raise Exception(f"No pages found for course '{chapter.name}'")

        PageMaterialCreator.regenerate(ai_client, self.topic, pages)
        PracticeSkillChallengeCreator.regenerate(ai_client, self.topic, pages)


    def regenerate_page(self, record: Page):
        ai_client = OpenAiHandler(f"Page Regeneration")
        return PageMaterialCreator.regenerate(ai_client, self.topic, [record])


    def regenerate_content(self, record: Course | Chapter | Page):
        if isinstance(record, Course):
            return self.regenerate_course()

        elif isinstance(record, Chapter):
            return self.regenerate_chapter()

        elif isinstance(record, Page):
            return self.regenerate_page()

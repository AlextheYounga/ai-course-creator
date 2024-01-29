from src.llm.openai_handler import OpenAiHandler
from src.creator.challenges.practice_skill_challenge_creator import PracticeSkillChallengeCreator
from src.creator.challenges.final_skill_challenge_creator import FinalSkillChallengeCreator
from src.creator.pages.page_material_creator import PageMaterialCreator
from db.db import DB, Topic, Course, Chapter, Page


class Regenerator:
    def __init__(self, record: Course | Chapter | Page):
        self.record = record
        self.topic = DB.query(Topic).filter(Topic.id == record.topic_id).first()


    def regenerate_course(self):
        course = self.record

        pages = DB.query(Page).filter(
            Topic.id == Page.topic_id,
            Page.course_slug == course.slug,
        ).all()

        if len(pages) == 0:
            raise Exception(f"No pages found for course '{course.name}'")

        self._regenerate_lesson_pages(pages)
        self._regenerate_challenge_pages(pages)
        self._regenerate_final_skill_challenge(course)


    def regenerate_chapter(self):
        chapter = self.record

        if chapter.content_type == 'final-skill-challenge':
            course = DB.query(Course).filter(
                Course.topic_id == self.topic.id,
                Course.slug == chapter.course_slug
            ).first()

            return self._regenerate_final_skill_challenge(course)

        pages = DB.query(Page).filter(
            Topic.id == Page.topic_id,
            Page.course_slug == chapter.course_slug,
            Page.chapter_slug == chapter.slug
        ).all()

        if len(pages) == 0:
            raise Exception(f"No pages found for course '{chapter.name}'")

        self._regenerate_challenge_pages(pages)

        self._regenerate_challenge_pages(pages)


    def regenerate_page(self):
        page_creator = PageMaterialCreator(
            self.topic.name,
            OpenAiHandler(f"Page Regeneration")
        )

        page_creator.regenerate([self.record])


    def _regenerate_lesson_pages(self, pages: list[Page]):
        lesson_pages = [page for page in pages if page.type == 'page']
        if len(lesson_pages) == 0: return

        page_creator = PageMaterialCreator(
            self.topic.name,
            OpenAiHandler(f"Page Regeneration")
        )

        return page_creator.regenerate(lesson_pages)


    def _regenerate_challenge_pages(self, pages: list[Page]):
        challenge_pages = [page for page in pages if page.type == 'practice-skill-challenge']
        if len(challenge_pages) == 0: return

        challenge_creator = PracticeSkillChallengeCreator(
            self.topic.name,
            OpenAiHandler(f"Practice Skill Challenge Regeneration")
        )

        return challenge_creator.regenerate(challenge_pages)


    def _regenerate_final_skill_challenge(self, course: Course):
        fsc_creator = FinalSkillChallengeCreator(
            self.topic.name,
            OpenAiHandler(f"Final Skill Challenge Regeneration")
        )
        fsc_creator.regenerate(course)



    @staticmethod
    def regenerate_content(record: Course | Chapter | Page):
        regenerator = Regenerator(record)

        if isinstance(record, Course):
            return regenerator.regenerate_course()

        elif isinstance(record, Chapter):
            return regenerator.regenerate_chapter()

        elif isinstance(record, Page):
            return regenerator.regenerate_page()

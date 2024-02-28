from openai import OpenAI
from db.db import DB, Topic, Course, Outline, OutlineEntity, Page
from src.handlers.generate_lesson_page_handler import GenerateLessonPageHandler
from src.handlers.generate_practice_challenge_page_handler import GeneratePracticeChallengePageHandler
from src.handlers.generate_final_challenge_page_handler import GenerateFinalSkillChallengePageHandler


class GenerateCourse:
    def __init__(self, topic_id: int, llm: OpenAI, course: Course):
        self.topic = DB.get(Topic, topic_id)
        self.llm_handler = llm
        self.course = course
        self.outline = Outline.get_master_outline(DB, self.topic)


    def run(self):
        course_pages = self._get_course_pages()

        lesson_pages = self._generate_course_lesson_pages(course_pages)
        challenge_pages = self._generate_course_challenges(course_pages)
        final_challenge = self._generate_course_final_challenge(course_pages)

        return {
            'lesson_pages': lesson_pages,
            'challenge_pages': challenge_pages,
            'final_challenge': final_challenge,
        }


    def _generate_course_lesson_pages(self, pages: list[Page]):
        lesson_pages = [page for page in pages if page.type == 'lesson']
        llm_instance = self.llm_handler(f"Course Page Generation - {self.course.name}")
        handler = GenerateLessonPageHandler(self.topic.id, llm_instance, lesson_pages)
        return handler.handle()


    def _generate_course_challenges(self, pages: list[Page]):
        challenge_pages = [page for page in pages if page.type == 'challenge']
        llm_instance = self.llm_handler(f"Course Challenge Generation - {self.course.name}")
        handler = GeneratePracticeChallengePageHandler(self.topic.id, llm_instance, challenge_pages)
        return handler.handle()


    def _generate_course_final_challenge(self, pages: list[Page]):
        final_challenge_pages = [page for page in pages if page.type == 'final-skill-challenge']
        llm_instance = self.llm_handler(f"Course Final Challenge Generation - {self.course.name}")
        handler = GenerateFinalSkillChallengePageHandler(self.topic.id, llm_instance, final_challenge_pages)
        return handler.handle()


    def _get_course_pages(self):
        return DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == 'Page',
            Page.course_id == self.course.id,
            Page.active == True,
        ).all()

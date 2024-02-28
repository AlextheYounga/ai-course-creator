from openai import OpenAI
from db.db import DB, Topic, Chapter, Outline, OutlineEntity, Page
from src.handlers.generate_lesson_page_handler import GenerateLessonPageHandler
from src.handlers.generate_practice_challenge_page_handler import GeneratePracticeChallengePageHandler


class GenerateChapter:
    def __init__(self, topic_id: int, llm: OpenAI, chapter: Chapter):
        self.topic = DB.get(Topic, topic_id)
        self.llm_handler = llm
        self.chapter = chapter
        self.outline = Outline.get_master_outline(DB, self.topic)


    def run(self):
        chapter_pages = self._get_chapter_pages()

        lesson_pages = self._generate_course_lesson_pages(chapter_pages)
        challenge_pages = self._generate_course_challenges(chapter_pages)

        return {
            'lesson_pages': lesson_pages,
            'challenge_pages': challenge_pages,
        }


    def _generate_chapter_lesson_pages(self, pages: list[Page]):
        lesson_pages = [page for page in pages if page.type == 'page']
        llm_instance = self.llm_handler(f"Chapter Page Generation - {self.course.name}")
        handler = GenerateLessonPageHandler(self.topic.id, llm_instance, lesson_pages)
        return handler.handle()


    def _generate_chapter_challenges(self, pages: list[Page]):
        challenge_pages = [page for page in pages if page.type == 'challenge']
        llm_instance = self.llm_handler(f"Chapter Challenge Generation - {self.course.name}")
        handler = GeneratePracticeChallengePageHandler(self.topic.id, llm_instance, challenge_pages)
        return handler.handle()


    def _get_chapter_pages(self):
        return DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == 'Page',
            Page.course_slug == self.chapter.course_slug,
            Page.chapter_slug == self.chapter.slug,
            Page.active == True,
        ).all()

from openai import OpenAI
from db.db import DB, Topic, Page
from src.handlers.generate_lesson_page_handler import GenerateLessonPageHandler
from src.handlers.generate_practice_challenge_page_handler import GeneratePracticeChallengePageHandler
from src.handlers.generate_final_challenge_page_handler import GenerateFinalSkillChallengePageHandler


class GeneratePage:
    def __init__(self, topic_id: int, llm: OpenAI, page: Page):
        self.topic = DB.get(Topic, topic_id)
        self.llm_handler = llm
        self.page = page


    def run(self):
        handlers = {
            'lesson': GenerateLessonPageHandler,
            'challenge': GeneratePracticeChallengePageHandler,
            'final-skill-challenge': GenerateFinalSkillChallengePageHandler
        }

        llm_instance = self.llm_handler(f"Page Generation - {self.page.name}")
        handler = handlers[self.page.type](self.topic.id, llm_instance, [self.page])

        return handler.handle()

import logging
from typing import Optional
from unittest.mock import MagicMock
from src.openai.openai_handler import OpenAiHandler


EXPECTED_COURSE_OUTLINE_RESPONSE = open('test/fixtures/responses/course-outline.md').read()
EXPECTED_DRAFT_OUTLINE_RESPONSE = open('test/fixtures/responses/draft-outline.md').read()
EXPECTED_SKILLS_RESPONSE = open('test/fixtures/responses/skills.md').read()
EXPECTED_PAGE_RESPONSE = open('test/fixtures/responses/page.md').read()
EXPECTED_PRACTICE_SKILL_CHALLENGE_RESPONSE = open('test/fixtures/responses/practice-skill-challenge.md').read()
EXPECTED_FINAL_SKILL_CHALLENGE_RESPONSE = open('test/fixtures/responses/final-skill-challenge.md').read()

LOG_PATH = "test/out/logs"


class OpenAIMockService(OpenAiHandler):
    def __init__(self, session_name: str, response: Optional[str] = None):
        super().__init__(session_name)

        logging.basicConfig(
            filename=f"{LOG_PATH}/chat.log",
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(f"{self.model} {session_name}")
        self.client = MagicMock()
        self.response = response

    def send_prompt(self, name: str, messages: list[dict], options: dict = {}):
        self.yaml_expected = options.get('yamlExpected', False)

        response = self.response
        if not response:
            if name == 'skills':
                response = EXPECTED_SKILLS_RESPONSE
            if name == 'draft-outline':
                response = EXPECTED_DRAFT_OUTLINE_RESPONSE
            if name == 'optimize-outline':
                response = EXPECTED_COURSE_OUTLINE_RESPONSE
            if name == 'page-material':
                response = EXPECTED_PAGE_RESPONSE
            if name == 'practice-skill-challenge':
                response = EXPECTED_PRACTICE_SKILL_CHALLENGE_RESPONSE
            if name == 'final-skill-challenge':
                response = EXPECTED_FINAL_SKILL_CHALLENGE_RESPONSE

        self.client.completion.choices[0].message.content = response
        completion = self.client.completion

        response_validated = self.response_validator(name, messages, completion, options)

        return response_validated

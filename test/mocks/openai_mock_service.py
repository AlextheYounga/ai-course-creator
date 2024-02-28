import logging
import random
from typing import Optional
from termcolor import colored
from unittest.mock import MagicMock
from services.openai_service import OpenAiService
from src.llm.token_counter import count_tokens_using_encoding
import markdown
from bs4 import BeautifulSoup


EXPECTED_MASTER_OUTLINE_RESPONSE = open('test/fixtures/responses/master-outline.md').read()
EXPECTED_SKILLS_RESPONSE = open('test/fixtures/responses/skills.md').read()
EXPECTED_PAGE_RESPONSE = open('test/fixtures/responses/page.md').read()
EXPECTED_PAGE_SUMMARY_RESPONSE = open('test/fixtures/responses/summary.md').read()
EXPECTED_PRACTICE_SKILL_CHALLENGE_RESPONSE = open('test/fixtures/responses/practice-skill-challenge.md').read()
EXPECTED_FINAL_SKILL_CHALLENGE_RESPONSE = open('test/fixtures/responses/final-skill-challenge.md').read()

LOG_PATH = "test/out/logs"


class OpenAiMockService(OpenAiService):
    def __init__(self, session_name: str, response: Optional[str] = None):
        super().__init__(session_name)

        logging.basicConfig(
            filename=f"{LOG_PATH}/chat.log",
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(f"Test {session_name}")
        self.client = MagicMock()
        self.response = response
        self.chunk_outline_calls = 0

    def send_prompt(self, name: str, messages: list[dict], options: dict = {}):
        self.yaml_expected = options.get('yamlExpected', False)

        tokens = count_tokens_using_encoding('gpt-3.5-turbo-0301', messages)
        for message in messages:
            if message['role'] == 'user':
                prompt = message['content']
                print(colored(f"Sending {name} - tokens: {tokens} - prompt: {prompt[:100]}...", "cyan"))
                break

        response = self.response
        if not response:
            if name == 'skills':
                response = EXPECTED_SKILLS_RESPONSE

            if name == 'outline-chunk':
                call = self.chunk_outline_calls + 1
                self.chunk_outline_calls = call
                response = open(f"test/fixtures/responses/outline-chunks/outline-chunk-{call}.md").read()

            if name == 'master-outline':
                response = EXPECTED_MASTER_OUTLINE_RESPONSE

            if name == 'page-material':
                hash = random.getrandbits(128)
                material = str(hash) + "\n" + EXPECTED_PAGE_RESPONSE
                response = material

            if name == 'summarize-page':
                response = EXPECTED_PAGE_SUMMARY_RESPONSE

            if name == 'practice-skill-challenge':
                hash = random.getrandbits(128)
                material = str(hash) + "\n" + EXPECTED_PRACTICE_SKILL_CHALLENGE_RESPONSE
                response = material

            if name == 'final-skill-challenge':
                hash = random.getrandbits(128)
                material = str(hash) + "\n" + EXPECTED_PRACTICE_SKILL_CHALLENGE_RESPONSE
                response = material

        self.client.completion.choices[0].message.content = response
        completion = self.client.completion

        response_validated = self.response_validator(name, messages, completion, options)

        return response_validated

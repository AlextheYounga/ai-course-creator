import random
from typing import Optional
from termcolor import colored
from unittest.mock import MagicMock

EXPECTED_MASTER_OUTLINE_RESPONSE = open('test/fixtures/responses/master-outline.md').read()
EXPECTED_SKILLS_RESPONSE = open('test/fixtures/responses/skills.md').read()
EXPECTED_PAGE_RESPONSE = open('test/fixtures/responses/page.md').read()
EXPECTED_PAGE_SUMMARY_RESPONSE = open('test/fixtures/responses/summary.md').read()
EXPECTED_PRACTICE_SKILL_CHALLENGE_RESPONSE = open('test/fixtures/responses/practice-skill-challenge.md').read()
EXPECTED_FINAL_SKILL_CHALLENGE_RESPONSE = open('test/fixtures/responses/final-skill-challenge.md').read()


class OpenAiMockService:
    def __init__(self, response: Optional[str] = None):
        self.response = response
        self.chunk_outline_calls = 0
        self.mock = MagicMock()

    def send_prompt(self, prompt):
        subject = prompt.subject
        print(colored(f"Sending {subject} - prompt: {prompt.content[:100]}...", "cyan"))

        response = self.response
        if not response:
            if subject == 'skills':
                response = EXPECTED_SKILLS_RESPONSE

            if subject == 'outline':
                call = self.chunk_outline_calls + 1
                self.chunk_outline_calls = call
                response = open(f"test/fixtures/responses/outline-chunks/outline-chunk-{call}.md").read()

            if subject == 'master-outline':
                response = EXPECTED_MASTER_OUTLINE_RESPONSE

            if subject == 'page-material':
                hash = random.getrandbits(128)
                material = str(hash) + "\n" + EXPECTED_PAGE_RESPONSE
                response = material

            if subject == 'summarize-page':
                response = EXPECTED_PAGE_SUMMARY_RESPONSE

            if subject == 'practice-skill-challenge':
                hash = random.getrandbits(128)
                material = str(hash) + "\n" + EXPECTED_PRACTICE_SKILL_CHALLENGE_RESPONSE
                response = material

            if subject == 'final-skill-challenge':
                hash = random.getrandbits(128)
                material = str(hash) + "\n" + EXPECTED_PRACTICE_SKILL_CHALLENGE_RESPONSE
                response = material

        response_object = self._completion_response_object(response)
        completion = self._mock_object(response_object)
        completion.model_dump_json.return_value = response_object

        return completion


    def _completion_response_object(self, response: str):
        return {
            "id": "chatcmpl-8sGWB9sJPlqkQ4BSQees3E9T9Sj7F",
            "choices": [
                {
                    "finish_reason": "stop",
                    "index": 0,
                    "logprobs": None,
                    "message": {
                        "content": response,
                        "role": "assistant",
                        "function_call": None,
                        "tool_calls": None
                    }
                }
            ],
            "created": 1707943899,
            "model": "gpt-3.5-turbo-0301",
            "object": "chat.completion",
            "system_fingerprint": "fp_f084bcfc79",
            "usage": {
                "completion_tokens": 611,
                "prompt_tokens": 4410,
                "total_tokens": 5021
            }
        }

    def _mock_object(self, data):
        for key, value in data.items():
            if isinstance(value, list):
                self.mock.configure_mock(**{
                    key: [self._mock_object(item) for item in value],
                })
            elif isinstance(value, dict):
                self.mock.configure_mock(**{
                    key: self._mock_object(value),
                })
            else:
                self.mock.configure_mock(**{
                    key: value,
                })
        return self.mock

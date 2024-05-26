import random
import json
from typing import Optional
from src.services.openai_client import OpenAiClient
from unittest.mock import MagicMock

EXPECTED_MASTER_OUTLINE_RESPONSE = open('test/fixtures/responses/master-outline.md').read()
EXPECTED_SKILLS_RESPONSE = open('test/fixtures/responses/skills.md').read()
EXPECTED_PAGE_RESPONSE = open('test/fixtures/responses/page.md').read()
EXPECTED_PAGE_SUMMARY_RESPONSE = open('test/fixtures/responses/summary.md').read()
EXPECTED_MULTIPLE_CHOICE_RESPONSE = open('test/fixtures/responses/interactives/multiple-choice.md').read()
EXPECTED_CODE_EDITOR_RESPONSE = open('test/fixtures/responses/interactives/code-editor.md').read()
EXPECTED_CODEPEN_RESPONSE = open('test/fixtures/responses/interactives/codepen.md').read()



class OpenAiMockClient(OpenAiClient):
    def __init__(self, response: Optional[str] = None):
        super()
        self.response = response
        self.mock = MagicMock()

    def chat_completion(self, prompt, params={}):
        subject = prompt.subject
        response = self.response
        if response: return response

        match subject:
            case 'skills':
                response = EXPECTED_SKILLS_RESPONSE

            case 'outline':
                outline_chunk_file = prompt.id - 1
                response = open(f"test/fixtures/responses/outline-chunks/outline-chunk-{outline_chunk_file}.md").read()

            case 'master-outline':
                response = EXPECTED_MASTER_OUTLINE_RESPONSE

            case 'page-material':
                hash = random.getrandbits(128)
                material = str(hash) + "\n" + EXPECTED_PAGE_RESPONSE
                response = material

            case 'summarize-page':
                response = EXPECTED_PAGE_SUMMARY_RESPONSE

            case 'multiple-choice':
                count = int(prompt.content.split('Prompt: please generate ')[1][0])
                multiple_choice_interactives = []
                for _ in range(count):
                    hash = random.getrandbits(128)
                    interactive_shortcode = EXPECTED_MULTIPLE_CHOICE_RESPONSE.replace('[multipleChoice', f'[multipleChoice hash="{hash}"')
                    multiple_choice_interactives.append(interactive_shortcode)
                response = "\n\n".join(multiple_choice_interactives)

            case 'code-editor':
                hash = random.getrandbits(128)
                response = EXPECTED_CODE_EDITOR_RESPONSE.replace('[codeEditor', f'[codeEditor hash="{hash}"')

            case 'codepen':
                hash = random.getrandbits(128)
                response = EXPECTED_CODEPEN_RESPONSE.replace('[codepen', f'[codepen hash="{hash}"')

        response_object = self._completion_response_object(response)
        completion = self._mock_object(response_object)
        completion.model_dump_json.return_value = json.dumps(response_object)

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

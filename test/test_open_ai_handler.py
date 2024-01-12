import os
import shutil
from src.openai.openai_handler import OpenAiHandler
from unittest.mock import MagicMock
import logging

LOG_PATH = "test/out/logs"

class MockOpenAi(OpenAiHandler):
    def __init__(self, session_name: str, response: str):
        super().__init__(session_name)
        self.client = MagicMock()

        logging.basicConfig(
            filename=f"{LOG_PATH}/chat.log",
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(f"{self.model} {session_name}")
        self.response = response
    
    def send_prompt(self, name: str, messages: list[dict], options: dict = {}):
        self.client.completion.choices[0].message.content = self.response
        completion = self.client.completion
        response_validated = self.response_validator(name, messages, completion, options)
        return response_validated



def _setup_test():
    if (os.path.exists(LOG_PATH)):
        shutil.rmtree(LOG_PATH)

    os.makedirs(LOG_PATH)
    open(f"{LOG_PATH}/chat.log", 'w').close()



def test_open_ai_handler_bad_response():
    _setup_test()

    mock_response = open('test/fixtures/responses/bad-yaml-response.md').read()

    open_ai_handler = MockOpenAi("test", mock_response)
    validated_response = open_ai_handler.send_prompt("test", [], {'yamlExpected': True})
    parsed_yaml = validated_response['dict']
    assert len(parsed_yaml) == 2


def test_open_ai_handler_hopeless_response():
    _setup_test()

    mock_response = open('test/fixtures/responses/hopeless-yaml-response.md').read()

    open_ai_handler = MockOpenAi("test", mock_response)
    hopeless_response = open_ai_handler.send_prompt("test", [], {'yamlExpected': True})
    assert hopeless_response['valid'] == False
    assert open_ai_handler.retry_count == 3


def test_open_ai_handler_good_response():
    _setup_test()

    mock_response = open('test/fixtures/responses/good-yaml-response.md').read()

    open_ai_handler = MockOpenAi("test", mock_response)
    good_response = open_ai_handler.send_prompt("test", [], {'yamlExpected': True})

    assert good_response['valid'] == True
    assert len(good_response['dict']) == 2
    assert isinstance(good_response['yaml'], str)
    assert "```" not in good_response['yaml']

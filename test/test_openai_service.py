from .mocks.db import *
from .mocks.openai_mock_service import OpenAiMockService
from src.llm.get_llm_client import get_llm_client



def test_get_llm_client():
    client = get_llm_client()
    assert client is not None
    assert client.__class__.__name__ == 'OpenAiMockService'


def test_open_ai_handler_bad_response():
    prompt = Prompt(
        thread_id=1,
        outline_id=1,
        model='gpt-3.5-turbo-0301',
        subject='generate-skills',
        estimated_tokens=42,
        content="Test",
    )

    mock_response = open('test/fixtures/responses/bad-yaml-response.md').read()

    open_ai_handler = OpenAiMockService(mock_response)
    completion = open_ai_handler.send_prompt(prompt)

    assert completion is not None

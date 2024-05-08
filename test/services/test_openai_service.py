from ..mocks.mock_db import *
from ..mocks.openai_mock_client import OpenAiMockClient
from src.utils.llm.get_llm_client import get_llm_client



def test_get_llm_client():
    client = get_llm_client()
    assert client is not None
    assert client.__class__.__name__ == 'OpenAiMockClient'


def test_open_ai_handler_bad_response():
    prompt = Prompt(
        outline_id=1,
        model='gpt-3.5-turbo-0301',
        subject='generate-skills',
        estimated_tokens=42,
        content="Test",
        properties={}
    )

    mock_response = open('test/fixtures/responses/bad-yaml-response.md').read()

    open_ai_handler = OpenAiMockClient(mock_response)
    completion = open_ai_handler.send_prompt(prompt)

    assert completion is not None

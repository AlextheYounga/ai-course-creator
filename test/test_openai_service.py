from .mocks.openai_mock_service import OpenAiMockService
from src.llm.get_llm_client import get_llm_client


def test_get_llm_client():
    client = get_llm_client()
    assert client is not None
    assert client.__class__.__name__ == 'OpenAiMockService'
    assert client.send_prompt("GenerateSkills", []) is not None


def test_open_ai_handler_bad_response():
    mock_response = open('test/fixtures/responses/bad-yaml-response.md').read()

    open_ai_handler = OpenAiMockService(mock_response)
    completion = open_ai_handler.send_prompt("GenerateSkills", [])

    assert completion is not None

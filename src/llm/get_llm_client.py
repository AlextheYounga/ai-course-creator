import os


def get_llm_client(client_args: dict = {}):
    env = os.getenv('APP_ENV', 'testing')
    llm = os.getenv('LLM', 'OPENAI')

    if env == 'development':
        if llm == 'OPENAI':
            from ..services.openai_service import OpenAiService
            return OpenAiService(*client_args)

    if env == 'testing':
        if llm == 'OPENAI':
            from test.mocks.openai_mock_service import OpenAiMockService
            return OpenAiMockService(*client_args)

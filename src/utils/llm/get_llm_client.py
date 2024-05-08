import os


def get_llm_client(client_args: dict = {}):
    env = os.getenv('APP_ENV', 'testing')
    llm = os.getenv('LLM', 'OPENAI')

    if env == 'testing':
        if llm == 'OPENAI':
            from test.mocks.openai_mock_client import OpenAiMockClient
            return OpenAiMockClient(*client_args)

    if llm == 'OPENAI':
        from src.services.openai_client import OpenAiClient
        return OpenAiClient(*client_args)

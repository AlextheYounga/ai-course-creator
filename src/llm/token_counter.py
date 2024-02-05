
import os


def _messages_to_single_string(messages):
    prompt = ""
    for message in messages:
        prompt += message['content']

    return prompt


def count_tokens_using_encoding(messages: list) -> int:
    """
    This implementation is, although accurate, extremely slow.
    """
    import tiktoken

    model = os.environ.get("MODEL") or 'gpt-3.5-turbo-1106'
    encoding = None
    content = _messages_to_single_string(messages)

    try:
        encoding = tiktoken.encoding_for_model(model)
    except Exception as e:
        print(f"Error parsing tokens: {e}")

    num_tokens = len(encoding.encode(content))
    return num_tokens


def count_tokens_using_encoding(messages: list):
    """
    This approach is a simple, *fast estimation of the number of tokens in a prompt.    
    """
    content = _messages_to_single_string(messages)
    characters = len(content)

    tokens = characters / 4
    return tokens

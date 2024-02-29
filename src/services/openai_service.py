from dotenv import load_dotenv
from ..utils.log_handler import LOG_HANDLER
from src.utils.files import read_yaml_file
from ..llm.get_llm_params import get_llm_params
from ..llm.token_counter import count_tokens_using_encoding
import os
from termcolor import colored
from openai import OpenAI
from time import sleep

load_dotenv()


class OpenAiService:
    def __init__(self, params_file: str = 'params.yaml'):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.logger = LOG_HANDLER(self.__class__.__name__)
        self.params = read_yaml_file(params_file)
        self.retry_count = 0


    def send_prompt(self, event_name: str, messages: list[dict], options: dict = {}) -> OpenAI:
        prompt_params = get_llm_params(event_name)
        quiet = options.get('quiet', False)
        model = prompt_params['model']
        tokens = count_tokens_using_encoding(model, messages)

        if not quiet:
            for message in messages:
                if message['role'] == 'user':
                    prompt = message['content']
                    print(colored(f"Sending {event_name} - tokens: {tokens} - prompt: {prompt[:100]}...", "cyan"))
                    break


        completion = None
        try:
            self.logger.info(f"SEND: {event_name} - {model}")

            completion = self.client.chat.completions.create(
                messages=messages,
                **prompt_params
            )

            self.logger.info(f"RESPONSE: {event_name} - {model} - status: {completion['status']}")

            sleep(1)  # Give OpenAI a break

            return completion
        except Exception as e:
            print(colored(f"Unknown error from OpenAI: {e}", "red"))
            self.logger.info(f"RESPONSE: {event_name} - {model} - status: {e}")
            return None

from db.db import Prompt
from dotenv import load_dotenv
from ..utils.log_handler import LOG_HANDLER
from src.utils.files import read_yaml_file
from ..llm.get_llm_params import get_llm_params
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


    def send_prompt(self, prompt: Prompt) -> OpenAI:
        prompt_params = prompt.properties.get('params', get_llm_params(prompt.subject))
        messages = prompt.payload
        quiet = prompt_params.get('quiet', False)
        model = prompt_params['model']

        if not quiet:
            for message in messages:
                if message['role'] == 'user':
                    prompt = message['content']
                    print(colored(f"Sending {prompt.subject} - tokens: {prompt.estimated_tokens} - prompt: {prompt[:100]}...", "cyan"))
                    break


        completion = None
        try:
            self.logger.info(f"SEND: {prompt.subject} - {model}")

            completion = self.client.chat.completions.create(
                messages=messages,
                **prompt_params
            )

            self.logger.info(f"RESPONSE: {prompt.subject} - {model} - status: {completion['status']}")

            self.__handle_exponential_backoff(prompt)

            return completion

        except Exception as e:
            print(colored(f"Unknown error from OpenAI: {e}", "red"))
            self.logger.info(f"RESPONSE: {prompt.subject} - {model} - status: {e}")
            return None

    def __handle_exponential_backoff(self, prompt: Prompt):
        sleep_time = 10 * prompt.attempts

        if prompt.attempts == 0:
            sleep_time = 1

        sleep(sleep_time)

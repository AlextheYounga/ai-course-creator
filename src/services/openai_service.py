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
        self.params = read_yaml_file(params_file)

    def send_prompt(self, prompt: Prompt) -> OpenAI:
        prompt_properties = prompt.properties or {}
        prompt_params = prompt_properties.get('params', get_llm_params(prompt.subject))

        quiet = prompt_params.get('quiet', False)
        model = prompt_params['model']

        if not quiet:
            print(colored(f"Sending {prompt.subject} - tokens: {prompt.estimated_tokens} - prompt: {prompt.content[:100]}...", "cyan"))

        completion = None
        try:
            LOG_HANDLER.info(f"SEND: {prompt.subject} - {model}")
            completion = self.chat_completion(prompt, prompt_params)
            LOG_HANDLER.info(f"RESPONSE: {prompt.subject} - {model} - ID: {completion.id}")

            return completion

        except Exception as e:
            print(colored(f"Unknown error from OpenAI: {e}", "red"))
            LOG_HANDLER.info(f"RESPONSE: {prompt.subject} - {model} - status: {e}")
            return None


    def chat_completion(self, prompt: Prompt, params: dict):
        messages = prompt.payload

        completion = self.client.chat.completions.create(
            messages=messages,
            **params
        )

        self.__handle_exponential_backoff(prompt)

        return completion


    def __handle_exponential_backoff(self, prompt: Prompt):
        sleep_time = 10 * prompt.attempts

        if prompt.attempts == 0:
            sleep_time = 1

        sleep(sleep_time)

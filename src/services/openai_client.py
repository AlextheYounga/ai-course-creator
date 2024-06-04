import os
from termcolor import colored
from datetime import datetime
from openai import OpenAI
from time import sleep
from dotenv import load_dotenv
from db.db import DB, Prompt
from src.utils.files import read_yaml_file
from ..utils.llm.get_llm_params import get_llm_params

load_dotenv()


class OpenAiClient:
    def __init__(self, params_file: str = 'configs/params.yaml'):
        self.db = DB()
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.params = read_yaml_file(params_file)

    def send_prompt(self, prompt: Prompt) -> OpenAI:
        self.handle_prompt_delay()

        prompt_params = prompt.get_properties().get('params', get_llm_params(prompt.subject))

        completion = None
        try:
            completion = self.chat_completion(prompt, prompt_params)
            return completion

        except Exception as e:
            print(colored(f"Unknown error from OpenAI: {e}", "red"))
            return None


    def chat_completion(self, prompt: Prompt, params: dict):
        messages = prompt.payload

        completion = self.client.chat.completions.create(
            messages=messages,
            **params
        )

        self.handle_exponential_backoff(prompt)

        return completion


    def handle_prompt_delay(self):
        last_prompt = self.db.query(Prompt).order_by(Prompt.id.desc()).first()
        last_prompt_time = last_prompt.created_at.timestamp()

        current_time = datetime.now().timestamp()
        time_diff = current_time - last_prompt_time

        if time_diff < 1:
            sleep(1)


    def handle_exponential_backoff(self, prompt: Prompt):
        sleep_time = 10 * prompt.attempts

        if prompt.attempts <= 1:
            sleep_time = 1

        if sleep_time > 1:
            print(colored(f"Sleeping for {sleep_time} seconds. Prompt attempts: {prompt.attempts}", "yellow"))

        sleep(sleep_time)

import os
import json
import yaml
import re
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from src.utils.chat_helpers import parse_markdown
from time import sleep
import logging


load_dotenv()


class OpenAiHandler:
    def __init__(self, session_name: str):
        # Initialize logger
        self.log_path = "src/data/chat/logs"
        logging.basicConfig(
            filename=f"{self.log_path}/chat.log",
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

        # Initialize OpenAI
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = os.environ.get("MODEL") or 'gpt-3.5-turbo-1106'
        self.logger = logging.getLogger(f"{self.model} {session_name}")
    

    def send_prompt(self, messages: list[dict]) -> OpenAI:
        for message in messages:
            if message['role'] == 'user':
                prompt = message['content']
                print(colored(f"Sending prompt: {prompt[:100]}...", "cyan"))
                break

        self.logger.info(f"SEND: {json.dumps(messages)}")

        completion = None
        try:
            # Send to ChatGPT
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
        except Exception as e:
            print(f"Error creating course: {e}")
            return None

        self.logger.info(f"RESPONSE: {completion.model_dump_json()}")

        sleep(1)  # Give OpenAI a break

        return completion

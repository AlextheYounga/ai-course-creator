import os
import json
import re
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from src.utils.parse import parse_markdown
from time import sleep

load_dotenv()

class OpenAiHandler:
    def __init__(self):
        # Initialize OpenAI
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = os.environ.get("MODEL") or 'gpt-3.5-turbo-1106'
        self.payload_path = f"src/data/chat/payloads"
        self.reply_path = f"src/data/chat/replies"

    def parse_markdown_json(self, content: str) -> dict | list | None:
        try:
            soup = parse_markdown(content)
            code_block = soup.find("code").get_text()
            code = re.sub(r"^[^\[]*", "", code_block)
            json_content = json.loads(code)

            return json_content
        except Exception as e:
            print(f"Error parsing markdown: {e}")
            return None


    def send_prompt(self, messages) -> OpenAI:
        for message in messages:
            if message['role'] == 'user':
                print(colored(f"Sending prompt: {message['content']}", "cyan"))

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


        sleep(1)  # Give OpenAI a break
        return completion
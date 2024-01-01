import os
import json
import re
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from src.utils.parse import parse_markdown
from datetime import datetime
from time import sleep

load_dotenv()

class OpenAiHandler:
    def __init__(self):
        # Initialize OpenAI
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = os.environ.get("MODEL") or 'gpt-3.5-turbo-1106'
        self.prompt_payload_path = f"src/data/chat/payloads"

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


    def send_prompt(self, messages: list[dict]) -> OpenAI:
        for message in messages:
            if message['role'] == 'user':
                prompt = message['content']
                print(colored(f"Sending prompt: {prompt[:100]}...", "cyan"))
                break
        
        # Save prompt payload
        self.save_prompt_payload(messages)

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
    
    def save_prompt_payload(self, messages) -> None:
        # Check paths
        self.check_save_paths(self.prompt_payload_path)

        # Save prompt payload log
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        payload_file = f"{self.prompt_payload_path}/prompt-{timestamp}.json"
        with open(payload_file, 'w') as f:
            f.write(json.dumps(messages))
            f.close()

    def check_save_paths(self, path):
        if not (os.path.exists(path)):
            os.mkdir(path)
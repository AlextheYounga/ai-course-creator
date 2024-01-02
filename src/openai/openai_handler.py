import os
import json
import yaml
import re
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from src.utils.chat_helpers import parse_markdown
from datetime import datetime
from time import sleep


load_dotenv()

class OpenAiHandler:
    def __init__(self):
        # Initialize OpenAI
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = os.environ.get("MODEL") or 'gpt-3.5-turbo-1106'
        self.payload_path = f"src/data/chat/payloads"

    def parse_markdown_json_list(self, content: str) -> list[dict]:
        try:
            soup = parse_markdown(content)
            code_block = soup.find("code").get_text()
            code = re.sub(r"^[^\[]*", "", code_block)
            json_content = json.loads(code)

            return json_content
        except Exception as e:
            try:
                print(colored(f"JSON parsing failed, trying with yaml parser...", "yellow"))
                # Trying with yaml parser if json parser fails
                json_content = yaml.load(code)

                return json_content
            except Exception as e:
                print(colored(f"Error parsing markdown JSON: {e}", "yellow"))
                return None
            

    def save_response_markdown(self, completion: OpenAI, save_path: str, save_file_name: str) -> None:
        # Check paths
        self._check_save_paths(save_path)

        # Save reply
        response_content = completion.choices[0].message.content
        with open(f"{save_path}/{save_file_name}.md", 'w') as f:
            f.write(response_content)
            f.close()
        

    def send_prompt(self, messages: list[dict]) -> OpenAI:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        
        for message in messages:
            if message['role'] == 'user':
                prompt = message['content']
                print(colored(f"Sending prompt: {prompt[:100]}...", "cyan"))
                break
        
        self._save_prompt_payload(timestamp, messages)

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


        self._save_response_payload(timestamp, completion)

        sleep(1)  # Give OpenAI a break
        
        return completion
    

    def handle_send_json_prompt(self, messages: list[dict], retry=0):
        completion = self.send_prompt(messages)
        print(colored("Done.", "green"))

        # Parse outline
        response_content = completion.choices[0].message.content
        json_content = self.parse_markdown_json_list(response_content)

        # If JSON fails to parse, retry
        if (json_content == None):
            if (retry < 3):
                print(colored("Retrying...", "yellow"))
                retry += 1
                self.handle_send_json_prompt(messages, retry)
            else:
                print(colored("Failed to parse JSON.", "red"))
                return []

        return completion, json_content
    
    
    def _save_prompt_payload(self, timestamp: str, messages: list[dict]) -> None:
        # Check paths
        self._check_save_paths(self.payload_path)

        # Save prompt payload log
        payload_file = f"{self.payload_path}/prompt-{timestamp}.json"
        with open(payload_file, 'w') as f:
            f.write(json.dumps(messages))
            f.close()

    def _save_response_payload(self, timestamp: str, completion: OpenAI) -> None:
        # Check paths
        self._check_save_paths(self.payload_path)

        # Save payload log
        payload_file = f"{self.payload_path}/response-{timestamp}.json"
        with open(payload_file, 'w') as f:
            f.write(completion.model_dump_json())
            f.close()

    def _check_save_paths(self, path):
        if not (os.path.exists(path)):
            os.makedirs(path, exist_ok=True)
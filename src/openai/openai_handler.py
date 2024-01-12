import os
import json
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from time import sleep
import markdown
from bs4 import BeautifulSoup
import logging
import yaml
import re


load_dotenv()


class OpenAiHandler:
    def __init__(self, session_name: str):
        # Initialize logger
        logging.basicConfig(
            filename="data/logs/chat.log",
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

        # Initialize OpenAI
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = os.environ.get("MODEL") or 'gpt-3.5-turbo-1106'
        self.logger = logging.getLogger(f"{self.model} {session_name}")
        self.retry_count = 0


    def send_prompt(self, name: str, messages: list[dict], options: dict = {}) -> OpenAI:
        quiet = options.get('quiet', False)

        if not quiet:
            for message in messages:
                if message['role'] == 'user':
                    prompt = message['content']
                    print(colored(f"Sending {name} prompt: {prompt[:100]}...", "cyan"))
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
            print(colored(f"Unknown error from OpenAI: {e}", "red"))
            return None

        self.logger.info(f"RESPONSE: {completion.model_dump_json()}")

        response_validated = self.response_validator(name, messages, completion, options)

        sleep(1)  # Give OpenAI a break

        return response_validated


    def response_validator(self, name: str, messages: list[dict], completion: OpenAI, options: dict):
        validate_response = {
            'valid': False,
            'content': None,
            'yaml': None,
            'dict': None
        }

        yaml_expected = options.get('yamlExpected', False)

        if completion.choices[0].message.content:
            content = completion.choices[0].message.content
            validate_response['content'] = content

            if yaml_expected:
                try:
                    html = markdown.markdown(content, extensions=['fenced_code'])
                    soup = BeautifulSoup(html, 'html.parser')
                    code_block = soup.find('code')
                    yaml_content = code_block.get_text()
                    validate_response['yaml'] = yaml_content
                    validate_response['dict'] = yaml.safe_load(yaml_content)

                except yaml.scanner.ScannerError as e:
                    try: 
                        print(colored(f"Failed to parse YAML content; attempting to repair content...", "yellow"))
                        validate_response['dict'] = self.attempt_repair_yaml_content(yaml_content)

                        if validate_response['dict']:
                            print(colored(f"Repair successful.", "green"))

                    except Exception as e:
                        if self.retry_count < 3:
                            self.logger.error(f"Failed to parse YAML content {e}")
                            print(colored(f"Failed to parse YAML content; retrying...", "red"))
                            self.retry_count += 1
                            return self.send_prompt(name, messages, options)
                        else:
                            self.logger.error(f"YAML parsing impossible {e}")
                            print(colored(f"YAML parsing impossible; maximum retries exceeded. Aborting...", "red"))
                            return validate_response

            if len(content) < 200:
                if self.retry_count < 3:
                    print(colored("Shit response; retrying...", "red"))
                    self.retry_count += 1
                    return self.send_prompt(name, messages, options)

                print(colored("Failed to receive good response from OpenAI. Aborting...", "red"))
                return validate_response

            validate_response['valid'] = True
            return validate_response
        else:
            if self.retry_count < 3:
                print(colored("Malformed completion, unknown error; retrying...", "red"))
                self.logger.error("Malformed completion, unknown error")
                self.retry_count += 1
                return self.send_prompt(name, messages, options)
            
            self.logger.error("Malformed completion, unknown error. Maximum retries exceeded")
            print(colored("Malformed completion, unknown error. Maximum retries exceeded. Aborting...", "red"))
            return validate_response


    def attempt_repair_yaml_content(self, content):
        known_keys = ['course', 'chapter', 'pages', 'courseName', ' modules', 'name', 'skills', 'category']

        for line in content.splitlines():
            # Repair misplaced colons
            keys = re.findall(r'\b[a-zA-Z0-9]+\b(?=:)', line)
            for key in keys:
                if key in known_keys: continue
                value = key + ':'
                corrected_value = value.replace(':', ' -')
                content = content.replace(value, corrected_value)

        return yaml.safe_load(content)

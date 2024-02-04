import os
from db.db import DB, Prompt, Response
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
            filename="storage/logs/chat.log",
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

        # Initialize OpenAI
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = os.environ.get("MODEL") or 'gpt-3.5-turbo-1106'
        self.logger = logging.getLogger(f"{session_name}")
        self.retry_count = 0


    def get_tokens(self, messages):
        prompt = ""
        for message in messages:
            prompt += message['content']

        characters = len(prompt)
        tokens = characters / 4

        return tokens


    def send_prompt(self, name: str, messages: list[dict], options: dict = {}) -> OpenAI:
        quiet = options.get('quiet', False)
        model = options.get('model', self.model)
        tokens = self.get_tokens(messages)

        properties = {
            **options,
            'maxTokens': options.get('maxTokens', None),
            'temperature': options.get('temperature', None),
        }

        if not quiet:
            for message in messages:
                if message['role'] == 'user':
                    prompt = message['content']
                    print(colored(f"Sending {name} - tokens: {tokens} - prompt: {prompt[:100]}...", "cyan"))
                    break


        self.logger.info(f"SEND: {model} - {json.dumps(messages)}")
        prompt_id = self.save_prompt(name, messages, tokens, properties)

        completion = None
        try:
            # Send to ChatGPT
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=properties['maxTokens'],
                temperature=properties['temperature'],
            )
        except Exception as e:
            print(colored(f"Unknown error from OpenAI: {e}", "red"))
            return None

        self.logger.info(f"RESPONSE: {model} - {completion.model_dump_json()}")
        self.save_response(prompt_id, completion, options)

        response_validated = self.response_validator(name, messages, completion, properties)

        sleep(1)  # Give OpenAI a break

        return response_validated


    def save_prompt(self, name: str, messages: list[dict], tokens: int, options: dict) -> int:
        content = ""
        for message in messages:
            content += message['content'] + "\n\n"

        prompt = Prompt(
            action=name,
            model=options.get('model', self.model),
            content=content,
            payload=messages,
            estimated_tokens=tokens,
            properties=options,
        )
        DB.add(prompt)
        DB.commit()

        return prompt.id


    def save_response(self, prompt_id: int, completion: OpenAI, options: dict) -> None:
        response = Response(
            prompt_id=prompt_id,
            role=completion.choices[0].message.role,
            model=completion.model,
            completion_tokens=completion.usage.completion_tokens,
            prompt_tokens=completion.usage.prompt_tokens,
            total_tokens=completion.usage.total_tokens,
            content=completion.choices[0].message.content,
            payload=json.loads(completion.model_dump_json()),
            properties=options,
        )
        DB.add(response)
        DB.commit()


    def response_validator(self, name: str, messages: list[dict], completion: OpenAI, options: dict):
        validate_response = {
            'valid': False,
            'content': None,
            'yaml': None,
            'dict': None
        }

        # Check to see if we're expecting a block of yaml data
        yaml_expected = options.get('yamlExpected', False)

        if completion.choices[0].message.content:
            content = completion.choices[0].message.content
            validate_response['content'] = content

            if yaml_expected:
                try:
                    validate_response = self.try_parse_yaml(validate_response, content)
                except Exception as e:
                    if self.retry_count < 3:
                        self.logger.error(f"Failed to parse YAML content {e}")
                        print(colored(f"Failed to parse YAML content; retrying...", "red"))
                        self.retry_count += 1
                        return self.send_prompt(name, messages, options)
                    else:
                        self.logger.error(f"YAML parsing impossible: {e}")
                        print(colored(f"YAML parsing impossible; maximum retries exceeded. Aborting...", "red"))
                        return validate_response

            if len(content) < 200:
                if self.retry_count < 3:
                    print(colored("Shit response; retrying...", "red"))
                    self.retry_count += 1
                    return self.send_prompt(name, messages, options)

                print(colored("Failed to receive good response from OpenAI. Aborting...", "red"))
                return validate_response

            # If here, all checks passed
            validate_response['valid'] = True
            self.retry_count = 0
            return validate_response


        if self.retry_count < 3:
            print(colored("Malformed completion, unknown error; retrying...", "red"))
            self.logger.error("Malformed completion, unknown error")
            self.retry_count += 1
            return self.send_prompt(name, messages, options)

        self.logger.error("Malformed completion, unknown error. Maximum retries exceeded")
        print(colored("Malformed completion, unknown error. Maximum retries exceeded. Aborting...", "red"))
        return validate_response



    def try_parse_yaml(self, return_object: dict, content: str):
        try:
            html = markdown.markdown(content, extensions=['fenced_code'])
            soup = BeautifulSoup(html, 'html.parser')
            code_block = soup.find('code')
            yaml_content = code_block.get_text()
            return_object['yaml'] = yaml_content
            return_object['dict'] = yaml.safe_load(yaml_content)

            return return_object

        except yaml.scanner.ScannerError:
            print(colored(f"Failed to parse YAML content; attempting to repair content...", "yellow"))

            return_object['dict'] = self.attempt_repair_yaml_content(yaml_content)

            if return_object['dict']: print(colored(f"Repair successful.", "green"))
            return return_object


    def attempt_repair_yaml_content(self, content):
        known_keys = ['course', 'chapter', 'pages', 'courseName', 'modules', 'name', 'skills', 'category']

        for line in content.splitlines():
            # Repair misplaced colons
            keys = re.findall(r'\b[a-zA-Z0-9]+\b(?=:)', line)
            for key in keys:
                if key in known_keys: continue
                value = key + ':'
                corrected_value = value.replace(':', ' -')
                content = content.replace(value, corrected_value)
        return yaml.safe_load(content)

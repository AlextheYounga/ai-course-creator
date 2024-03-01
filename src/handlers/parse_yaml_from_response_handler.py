from db.db import DB, Response
from ..utils.log_handler import LOG_HANDLER
from termcolor import colored
import markdown
import yaml
import re
from bs4 import BeautifulSoup



class ParseYamlFromResponseHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.response = DB.get(Response, data['responseId'])
        self.yaml_content = ''
        self.logger = LOG_HANDLER(self.__class__.__name__)


    def handle(self):
        content = self.response.payload['choices'][0]['message']['content']

        try:
            html = markdown.markdown(content, extensions=['fenced_code'])
            soup = BeautifulSoup(html, 'html.parser')
            code_block = soup.find('code')

            self.yaml_content = code_block.get_text()
            yaml_dict = yaml.safe_load(self.yaml_content)

            return {'yaml': self.yaml_content, 'dict': yaml_dict, 'error': None}

        except yaml.scanner.ScannerError:
            print(colored(f"Failed to parse YAML content; attempting to repair content...", "yellow"))

            try:
                yaml_dict = self._attempt_repair_yaml_content(self.yaml_content)
                print(colored(f"Repair successful.", "green"))

                return {'yaml': self.yaml_content, 'dict': yaml_dict, 'error': None}

            except Exception as e:
                return {'yaml': None, 'dict': None, 'error': e}


    def _attempt_repair_yaml_content(self, content):
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

from db.db import DB, Outline, Thread, Response
from ...utils.log_handler import LOG_HANDLER
from ..parse_yaml_from_response_handler import ParseYamlFromResponseHandler
from termcolor import colored
from sqlalchemy.orm.attributes import flag_modified




class ProcessGenerateSkillsResponseHandler:
    def __init__(self, thread_id: int, outline_id: int, response_id: int):
        self.thread = DB.get(Thread, thread_id)
        self.outline = DB.get(Outline, outline_id)
        self.response = DB.get(Response, response_id)
        self.prompt = self.response.prompt
        self.topic = self.outline.topic
        self.logger = LOG_HANDLER(self.__class__.__name__)


    def handle(self) -> Outline:
        completion = self.response.payload

        if not completion['choices'][0]['message']['content']:
            print(colored("Malformed completion, unknown error. Aborting...", "red"))
            # Retry

        content = completion['choices'][0]['message']['content']

        if len(content) < 200:
            print(colored("Shit response; retrying...", "red"))
            # Retry

        yaml_handler = ParseYamlFromResponseHandler(self.thread.id, content)
        yaml_data = yaml_handler.handle()
        skills_obj = yaml_data['dict']

        if yaml_data['error']:
            print(colored(f"Failed to parse YAML content; maximum retries exceeded. Aborting...", "red"))
            # Retry

        self._update_response_record(completion, yaml_data)
        self._save_skills_to_outline(skills_obj)

        return self.outline


    def _update_response_record(self, completion: dict, yaml_data: dict):
        properties = {
            'params': self.prompt.properties['params'],
            'yaml': yaml_data
        }

        self.response.role = completion['choices'][0]['message']['role']
        self.response.model = completion['model']
        self.response.prompt_tokens = completion['usage']['prompt_tokens']
        self.response.completion_tokens = completion['usage']['completion_tokens']
        self.response.total_tokens = completion['usage']['total_tokens']
        self.response.content = completion['choices'][0]['message']['content']
        self.response.properties = properties

        DB.commit()


    def _save_skills_to_outline(self, skills_obj: dict):
        outline_properties = self.outline.properties or {}

        properties = {
            **outline_properties,
            'skills': skills_obj
        }

        self.outline.properties = properties
        flag_modified(self.outline, "properties")

        DB.add(self.outline)
        DB.commit()

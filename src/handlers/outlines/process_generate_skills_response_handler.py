from db.db import DB, Outline, Response
from ...utils.log_handler import LOG_HANDLER
from ..validate_llm_response_handler import ValidateLLMResponseHandler
from ..parse_yaml_from_response_handler import ParseYamlFromResponseHandler
from .send_generate_skills_prompt_to_llm_handler import SendGenerateSkillsPromptToLLMHandler
from termcolor import colored
from sqlalchemy.orm.attributes import flag_modified



class ProcessGenerateSkillsResponseHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.response = DB.get(Response, data['responseId'])
        self.prompt = self.response.prompt
        self.topic = self.outline.topic
        self.logging = LOG_HANDLER(self.__class__.__name__)


    def handle(self) -> Outline:
        self.__log_event()

        completion = self.response.payload

        validated_response = ValidateLLMResponseHandler(
            self.thread_id,
            self.outline.id,
            self.response.id
        ).handle()

        if not validated_response:
            return False
            # Retry

        content = completion['choices'][0]['message']['content']

        yaml_handler = ParseYamlFromResponseHandler(self.thread_id, content)
        yaml_data = yaml_handler.handle()
        skills_obj = yaml_data['dict']

        if yaml_data['error']:
            print(colored(f"Failed to parse YAML content; maximum retries exceeded. Aborting...", "red"))
            SendGenerateSkillsPromptToLLMHandler(self.thread_id, self.outline.id, self.prompt.id).handle()

        self._save_skills_to_outline(skills_obj)

        return self.outline


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


    def __log_event(self):
        self.logging.info(f"Thread: {self.thread_id} - Outline: {self.outline.id}")

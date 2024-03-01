from db.db import DB, Outline, Response
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



    def handle(self) -> Outline:
        validated_response = ValidateLLMResponseHandler({
            'threadId': self.thread_id,
            'outlineId': self.outline.id,
            'responseId': self.response.id
        }).handle()

        if not validated_response:
            return False
            # Retry

        yaml_data = ParseYamlFromResponseHandler({
            'threadId': self.thread_id,
            'responseId': self.response.id
        }).handle()

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

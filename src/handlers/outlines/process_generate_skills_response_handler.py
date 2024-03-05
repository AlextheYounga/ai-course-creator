from db.db import DB, Outline, Response
from src.events.event_manager import EVENT_MANAGER
from src.events.events import GenerateSkillsResponseProcessedSuccessfully, InvalidGenerateSkillsResponseFromLLM, FailedToParseYamlFromGenerateSkillsResponse
from ..validate_llm_response_handler import ValidateLLMResponseHandler
from ..parse_yaml_from_response_handler import ParseYamlFromResponseHandler
from sqlalchemy.orm.attributes import flag_modified



class ProcessGenerateSkillsResponseHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.response = DB.get(Response, data['responseId'])
        self.prompt = self.response.prompt
        self.topic = self.outline.topic
        self.event_payload = {
            'threadId': self.thread_id,
            'outlineId': self.outline.id,
            'responseId': self.response.id,
            'topicId': self.topic.id,
            'promptId': self.prompt.id,
            **data
        }


    def handle(self) -> Outline:
        validated_response = ValidateLLMResponseHandler(self.event_payload).handle()

        if not validated_response:
            if self.prompt.attempts <= 3:
                raise Exception("Invalid response; maximum retries exceeded. Aborting...")

            # Retry
            self.prompt.increment_attempts(DB)
            return EVENT_MANAGER.trigger(InvalidGenerateSkillsResponseFromLLM(self.event_payload))

        yaml_data = ParseYamlFromResponseHandler(self.event_payload).handle()

        skills_obj = yaml_data['dict']

        if yaml_data['error']:
            if self.prompt.attempts <= 3:
                raise Exception("Failed to parse YAML content; maximum retries exceeded. Aborting...")

            # Retry
            self.prompt.increment_attempts(DB)
            return EVENT_MANAGER.trigger(FailedToParseYamlFromGenerateSkillsResponse(self.event_payload))

        self._save_skills_to_outline(skills_obj)

        return EVENT_MANAGER.trigger(
            GenerateSkillsResponseProcessedSuccessfully(self.event_payload)
        )


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

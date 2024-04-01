from db.db import DB, Outline, Response
from src.events.event_manager import EVENT_MANAGER
from src.events.events import GenerateSkillsResponseProcessedSuccessfully, InvalidGenerateSkillsResponseFromOpenAI, FailedToParseYamlFromGenerateSkillsResponse
from ..validate_response_from_openai_handler import ValidateResponseFromOpenAIHandler
from ..parse_yaml_from_response_handler import ParseYamlFromResponseHandler



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
        validated_response = ValidateResponseFromOpenAIHandler(self.event_payload).handle()

        if not validated_response:
            return EVENT_MANAGER.trigger(InvalidGenerateSkillsResponseFromOpenAI(self.event_payload))

        yaml_data = ParseYamlFromResponseHandler(self.event_payload).handle()

        skills_obj = yaml_data['dict']

        if yaml_data['error']:
            return EVENT_MANAGER.trigger(FailedToParseYamlFromGenerateSkillsResponse(self.event_payload))

        self.outline.update_properties(DB, {'skills': skills_obj})

        return EVENT_MANAGER.trigger(
            GenerateSkillsResponseProcessedSuccessfully(self.event_payload)
        )

from db.db import DB, Outline
from src.events.events import GenerateSkillsResponseProcessedSuccessfully, InvalidGenerateSkillsResponseFromOpenAI, FailedToParseYamlFromGenerateSkillsResponse
from .validate_response_from_openai_handler import ValidateResponseFromOpenAIHandler
from .parse_yaml_from_response_handler import ParseYamlFromResponseHandler



class ProcessGenerateSkillsResponseHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.outline = self.db.get(Outline, data['outlineId'])


    def handle(self) -> Outline:
        validated_response = ValidateResponseFromOpenAIHandler(self.data).handle()

        if not validated_response:
            return InvalidGenerateSkillsResponseFromOpenAI(self.data)

        yaml_data = ParseYamlFromResponseHandler(self.data).handle()

        skills_obj = yaml_data['dict']

        if yaml_data['error']:
            return FailedToParseYamlFromGenerateSkillsResponse(self.data)

        self.outline.update_properties(self.db, {'skills': skills_obj})

        return GenerateSkillsResponseProcessedSuccessfully(self.data)

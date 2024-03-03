from db.db import DB, Outline, Prompt, Response
from src.events.event_manager import EVENT_MANAGER
from src.events.events import AllOutlineChunkResponsesProcessed, InvalidOutlineChunkResponsesFromLLM, FailedToParseYamlFromOutlineChunkResponses
from ..validate_llm_response_handler import ValidateLLMResponseHandler
from ..parse_yaml_from_response_handler import ParseYamlFromResponseHandler
from sqlalchemy.orm.attributes import flag_modified



class ProcessGenerateOutlineChunksResponsesHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.prompts = DB.query(Prompt).filter(Prompt.id.in_(data['promptIds'])).all()
        self.responses = DB.query(Response).filter(Response.id.in_(data['responseIds'])).all()
        self.topic = self.outline.topic

    def handle(self) -> Outline:
        for response in self.responses:
            validated_response = ValidateLLMResponseHandler(self.__event_payload(response)).handle()

            if not validated_response:
                if response.prompt.attempts <= 3:
                    raise Exception("Invalid response; maximum retries exceeded. Aborting...")

                # Retry
                response.prompt.increment_attempts(DB)
                return EVENT_MANAGER.trigger(InvalidOutlineChunkResponsesFromLLM(self.__event_payload(response)))

            yaml_handler = ParseYamlFromResponseHandler(self.__event_payload(response))
            yaml_data = yaml_handler.handle()
            chunk_obj = yaml_data['dict']

            if yaml_data['error']:
                if response.prompt.attempts <= 3:
                    raise Exception("Failed to parse YAML content; maximum retries exceeded. Aborting...")

                # Retry
                response.prompt.increment_attempts(DB)
                return EVENT_MANAGER.trigger(FailedToParseYamlFromOutlineChunkResponses(self.__event_payload(response)))

            self._save_chunk_to_outline(chunk_obj)

        return self.__trigger_completion_event({
            'threadId': self.thread_id,
            'outlineId': self.outline.id,
            'responseIds': [response.id for response in self.responses],
            'topicId': self.topic.id,
            'promptIds': [prompt.id for prompt in self.prompts],
        })


    def _save_chunk_to_outline(self, chunk_obj: dict):
        outline_properties = self.outline.properties
        existing_outline_chunks = outline_properties.get('outlineChunks', [])
        updated_outline_chunks = existing_outline_chunks + chunk_obj

        properties = {
            **outline_properties,
            'outlineChunks': updated_outline_chunks
        }

        self.outline.properties = properties
        flag_modified(self.outline, "properties")

        DB.add(self.outline)
        DB.commit()

    def __event_payload(self, response: Response):
        return {
            'threadId': self.thread_id,
            'outlineId': self.outline.id,
            'responseId': response.id,
            'topicId': self.topic.id,
            'promptId': response.prompt.id,
        }

    def __trigger_completion_event(self, data: dict):
        EVENT_MANAGER.trigger(AllOutlineChunkResponsesProcessed(data))

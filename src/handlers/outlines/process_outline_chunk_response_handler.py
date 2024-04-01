from db.db import DB, Outline, Response
from src.events.event_manager import EVENT_MANAGER
from src.events.events import OutlineChunkResponseProcessedSuccessfully, InvalidOutlineChunkResponseFromOpenAI, FailedToParseYamlFromOutlineChunkResponse
from ..validate_response_from_openai_handler import ValidateResponseFromOpenAIHandler
from ..parse_yaml_from_response_handler import ParseYamlFromResponseHandler



class ProcessOutlineChunkResponseHandler:
    def __init__(self, data: dict):
        self.data = data
        self.outline = DB.get(Outline, data['outlineId'])
        self.response = DB.get(Response, data['responseId'])
        self.prompt = self.response.prompt



    def handle(self) -> Outline:
        validated_response = ValidateResponseFromOpenAIHandler(self.data).handle()

        if not validated_response:
            return EVENT_MANAGER.trigger(InvalidOutlineChunkResponseFromOpenAI(self.data))

        yaml_handler = ParseYamlFromResponseHandler(self.data)
        yaml_data = yaml_handler.handle()
        chunk_obj = yaml_data['dict']

        if yaml_data['error']:
            if self.prompt.attempts <= 3:
                raise Exception("Failed to parse YAML content; maximum retries exceeded. Aborting...")
            return EVENT_MANAGER.trigger(FailedToParseYamlFromOutlineChunkResponse(self.data))

        self._save_chunk_to_outline(chunk_obj)

        return EVENT_MANAGER.trigger(
            OutlineChunkResponseProcessedSuccessfully(self.data)
        )


    def _save_chunk_to_outline(self, chunk_obj: dict):
        existing_outline_chunks = self.outline.get_properties().get('outlineChunks', [])
        updated_outline_chunks = existing_outline_chunks + chunk_obj

        self.outline.update_properties(DB, {'outlineChunks': updated_outline_chunks})

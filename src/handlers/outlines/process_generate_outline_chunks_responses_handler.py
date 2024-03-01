from db.db import DB, Outline, Response
from ...utils.log_handler import LOG_HANDLER
from ..validate_llm_response_handler import ValidateLLMResponseHandler
from ..parse_yaml_from_response_handler import ParseYamlFromResponseHandler
from termcolor import colored
from sqlalchemy.orm.attributes import flag_modified



class ProcessGenerateOutlineChunksResponsesHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.responses = DB.query(Response).filter(Response.id.in_(data['responseIds'])).all()
        self.topic = self.outline.topic
        self.logging = LOG_HANDLER(self.__class__.__name__)


    def handle(self) -> Outline:
        self.__log_event()

        for response in self.responses:
            completion = response.payload

            validated_response = ValidateLLMResponseHandler(
                self.thread_id,
                self.outline.id,
                response.id
            ).handle()

            if not validated_response:
                return False
                # Retry

            content = completion['choices'][0]['message']['content']

            yaml_handler = ParseYamlFromResponseHandler(self.thread_id, response.id)
            yaml_data = yaml_handler.handle()
            chunk_obj = yaml_data['dict']

            if yaml_data['error']:
                print(colored(f"Failed to parse YAML content; maximum retries exceeded. Aborting...", "red"))
                # Retry

            self._save_chunk_to_outline(chunk_obj)

        return self.outline


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


    def __log_event(self):
        self.logging.info(f"Thread: {self.thread_id} - Outline: {self.outline.id}")

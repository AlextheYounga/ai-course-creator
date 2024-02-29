from db.db import DB, Outline, Thread, Response
from ...utils.log_handler import LOG_HANDLER
from ..parse_yaml_from_response_handler import ParseYamlFromResponseHandler
from termcolor import colored
from sqlalchemy.orm.attributes import flag_modified




class ProcessGenerateOutlineChunksResponsesHandler:
    def __init__(self, thread_id: int, outline_id: int, response_ids: list[int]):
        self.thread = DB.get(Thread, thread_id)
        self.outline = DB.get(Outline, outline_id)
        self.responses = DB.query(Response).filter(Response.id.in_(response_ids)).all()
        self.topic = self.outline.topic
        self.logger = LOG_HANDLER(self.__class__.__name__)


    def handle(self) -> Outline:
        for response in self.responses:
            completion = response.payload

            if not completion['choices'][0]['message']['content']:
                print(colored("Malformed completion, unknown error. Aborting...", "red"))
                # Retry

            content = completion['choices'][0]['message']['content']

            if len(content) < 200:
                print(colored("Shit response; retrying...", "red"))
                # Retry

            yaml_handler = ParseYamlFromResponseHandler(self.thread.id, content)
            yaml_data = yaml_handler.handle()
            chunk_obj = yaml_data['dict']

            if yaml_data['error']:
                print(colored(f"Failed to parse YAML content; maximum retries exceeded. Aborting...", "red"))
                # Retry

            self._save_chunk_to_outline(chunk_obj)
            response = self._update_response_record(response, completion, yaml_data)

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


    def _update_response_record(self, response: Response, completion: dict, yaml_data: dict):
        prompt = response.prompt

        properties = {
            'params': prompt.properties,
            'yaml': yaml_data
        }

        response.role = completion['choices'][0]['message']['role']
        response.model = completion['model']
        response.prompt_tokens = completion['usage']['prompt_tokens']
        response.total_tokens = completion['usage']['total_tokens']
        response.content = completion['choices'][0]['message']['content']
        response.properties = properties

        DB.commit()

        return response

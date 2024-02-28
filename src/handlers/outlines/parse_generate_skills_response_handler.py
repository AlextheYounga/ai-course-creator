from db.db import DB, Outline, Thread, Response
from ...utils.log_handler import LOG_HANDLER
from .parse_yaml_from_response_handler import ParseYamlFromResponseHandler
from termcolor import colored




class ParseGenerateSkillsResponseHandler:
    def __init__(self, thread_id: int, outline_id: int, response_id: int):
        self.thread = DB.get(Thread, thread_id)
        self.outline = DB.get(Outline, outline_id)
        self.response = DB.get(Response, response_id)
        self.prompt = self.response.prompt
        self.topic = self.outline.topic
        self.logger = LOG_HANDLER.getLogger(self.__name__.__name__)


    def handle(self) -> dict:
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

        if yaml_data['error']:
            print(colored(f"Failed to parse YAML content; maximum retries exceeded. Aborting...", "red"))
            # Retry

        self._save_parsed_response_to_db(completion, yaml_data)

        return self.response


    def _save_parsed_response_to_db(self, completion: dict, yaml_data: dict):
        properties = {
            'params': self.prompt.properties,
            'yaml': yaml_data
        }

        self.response.role = completion['choices'][0]['message']['role']
        self.response.model = completion['model']
        self.response.prompt_tokens = completion['usage']['prompt_tokens']
        self.response.total_tokens = completion['usage']['total_tokens']
        self.response.content = completion['choices'][0]['message']['content']
        self.response.properties = properties

        DB.commit()

        return self.response

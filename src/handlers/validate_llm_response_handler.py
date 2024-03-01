from db.db import DB, Outline, Response
from db.db import DB, Outline, Response
from ..utils.log_handler import LOG_HANDLER
from termcolor import colored
from sqlalchemy.orm.attributes import flag_modified




class ValidateLLMResponseHandler:
    def __init__(self, thread_id: int, outline_id: int, response_id: int):
        self.thread_id = thread_id
        self.outline = DB.get(Outline, outline_id)
        self.response = DB.get(Response, response_id)
        self.prompt = self.response.prompt
        self.topic = self.outline.topic
        self.logging = LOG_HANDLER(self.__class__.__name__)


    def handle(self) -> Outline:
        self.__log_event()
        completion = self.response.payload

        if not completion['choices'][0]['message']['content']:
            print(colored("Malformed completion, unknown error. Aborting...", "red"))
            return False  # Retry


        content = completion['choices'][0]['message']['content']

        if len(content) < 200:
            print(colored("Shit response; retrying...", "red"))
            return False  # Retry


        self._update_response_record(completion)

        return self.response


    def _update_response_record(self, completion: dict):
        properties = {
            'params': self.prompt.properties['params'],
        }

        self.response.role = completion['choices'][0]['message']['role']
        self.response.model = completion['model']
        self.response.prompt_tokens = completion['usage']['prompt_tokens']
        self.response.completion_tokens = completion['usage']['completion_tokens']
        self.response.total_tokens = completion['usage']['total_tokens']
        self.response.content = completion['choices'][0]['message']['content']
        self.response.properties = properties

        DB.commit()


    def __log_event(self):
        self.logging.info(f"Thread: {self.thread_id} - Outline: {self.outline.id}")

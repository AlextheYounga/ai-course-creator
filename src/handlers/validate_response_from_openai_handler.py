from termcolor import colored
from db.db import DB, Outline, Response


class ValidateResponseFromOpenAIHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.response = self.db.get(Response, data['responseId'])
        self.prompt = self.response.prompt


    def handle(self) -> Outline:
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

        self.db.commit()

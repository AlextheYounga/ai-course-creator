from db.db import DB, Outline, Thread, Prompt, Response
from .parse_generate_skills_response_handler import ParseGenerateSkillsResponseHandler
from ...utils.log_handler import LOG_HANDLER
from termcolor import colored
from openai import OpenAI
from openai.types.completion import Completion
import json



class SendGenerateSkillsPromptHandler:
    def __init__(self, thread_id: int, outline_id: int, prompt_id: int, llm: OpenAI):
        self.thread = DB.get(Thread, thread_id)
        self.outline = DB.get(Outline, outline_id)
        self.prompt = DB.get(Prompt, prompt_id)
        self.llm_handler = llm()
        self.topic = self.outline.topic
        self.logger = LOG_HANDLER.getLogger(self.__name__.__name__)


    def handle(self) -> dict:
        print(colored(f"\nGenerating {self.topic.name} skills...", "yellow"))

        messages = self.prompt.payload

        # Send to ChatGPT
        completion = self.llm_handler.send_prompt('generate-skills', messages)
        if completion == None:
            raise Exception("LLM completion failed. There is likely more output in the logs.")

        response = self._save_response_payload_to_db(completion)

        return response


    def _save_response_payload_to_db(self, completion: Completion):
        response = Response(
            prompt_id=self.prompt.id,
            role=completion.choices[0].message.role,
            payload=json.loads(completion.model_dump_json()),
        )
        DB.add(response)
        DB.commit()

        return response

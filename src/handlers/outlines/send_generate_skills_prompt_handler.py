from db.db import DB, Outline, Thread, Prompt, Response
from ...llm.get_llm_client import get_llm_client
from ...utils.log_handler import LOG_HANDLER
from termcolor import colored
from openai.types.completion import Completion
import json



class SendGenerateSkillsPromptHandler:
    def __init__(self, thread_id: int, outline_id: int, prompt_id: int):
        self.thread = DB.get(Thread, thread_id)
        self.outline = DB.get(Outline, outline_id)
        self.prompt = DB.get(Prompt, prompt_id)
        self.topic = self.outline.topic
        self.logger = LOG_HANDLER.getLogger(self.__class__.__name__)


    def handle(self):
        print(colored(f"\nGenerating {self.topic.name} skills...", "yellow"))

        messages = self.prompt.payload

        # Send to ChatGPT
        llm_client = get_llm_client()
        completion = llm_client.send_prompt('GenerateSkills', messages)

        if completion == None:
            raise Exception("LLM completion failed. There is likely more output in the logs.")

        response = self._save_response_payload_to_db(completion)

        return response


    def _save_response_payload_to_db(self, completion: Completion):
        # We only save the payload for now, we will process this later.
        response = Response(
            prompt_id=self.prompt.id,
            role=completion.choices[0].message.role,
            payload=json.loads(completion.model_dump_json()),
        )
        DB.add(response)
        DB.commit()

        return response

from db.db import DB, Outline, Prompt, Response
from ...llm.get_llm_client import get_llm_client
from ...utils.log_handler import LOG_HANDLER
from .process_generate_skills_response_handler import ProcessGenerateSkillsResponseHandler
from termcolor import colored
from openai.types.completion import Completion



class SendGenerateSkillsPromptToLLMHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.prompt = DB.get(Prompt, data['promptId'])
        self.topic = self.outline.topic
        self.logging = LOG_HANDLER(self.__class__.__name__)


    def handle(self) -> Response:
        self.__log_event()

        print(colored(f"\nGenerating {self.topic.name} skills...", "yellow"))

        messages = self.prompt.payload

        # Send to ChatGPT
        llm_client = get_llm_client()
        completion = llm_client.send_prompt('GenerateSkills', messages)

        if completion == None:
            raise Exception("LLM completion failed. There is likely more output in the logs.")

        response = self._save_response_payload_to_db(completion)

        response = ProcessGenerateSkillsResponseHandler(self.thread_id, self.outline.id, response.id).handle()

        return response


    def _save_response_payload_to_db(self, completion: Completion):
        # We only save the payload for now, we will process this later.
        response = Response(
            thread_id=self.thread_id,
            outline_id=self.outline.id,
            prompt_id=self.prompt.id,
            role=completion.choices[0].message.role,
            payload=completion.model_dump_json(),
        )

        DB.add(response)
        DB.commit()

        return response

    def __log_event(self):
        self.logging.info(f"Thread: {self.thread_id} - Outline: {self.outline.id}")

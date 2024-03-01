from db.db import DB, Page, Outline, Prompt, Response
from ...utils.log_handler import LOG_HANDLER
from ...llm.get_llm_client import get_llm_client
from .create_lesson_page_prompt_handler import CreateLessonPagePromptHandler
from openai.types.completion import Completion



class SendGenerateLessonPagePromptToLLMHandler:
    def __init__(self, thread_id: int, outline_id: int, page_id: int):
        self.thread_id = thread_id
        self.outline = DB.get(Outline, outline_id)
        self.page = DB.get(Page, page_id)
        self.topic = self.outline.topic
        self.logging = LOG_HANDLER(self.__class__.__name__)


    def handle(self):
        self.__log_event()

        # Build prompt
        prompt_handler = CreateLessonPagePromptHandler(self.thread_id, self.outline, self.page)
        prompt = prompt_handler.handle()
        messages = prompt.payload

        # Send to ChatGPT
        llm_client = get_llm_client()
        completion = llm_client.send_prompt('GenerateLesson', messages)

        if completion == None:
            raise Exception("LLM completion failed. There is likely more output in the logs.")

        response = self._save_response_payload_to_db(prompt, completion)

        return response


    def _save_response_payload_to_db(self, prompt: Prompt, completion: Completion):
        # We only save the payload for now, we will process this later.
        response = Response(
            thread_id=self.thread_id,
            outline_id=self.outline.id,
            prompt_id=prompt.id,
            role=completion.choices[0].message.role,
            payload=completion.model_dump_json(),
        )

        DB.add(response)
        DB.commit()

        return response


    def __log_event(self):
        self.logging.info(f"Thread: {self.thread_id} - Outline: {self.outline.id} - Page: {self.page.id}")

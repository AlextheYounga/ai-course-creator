from db.db import DB, Page, Outline, OutlineEntity, Prompt, Response
from ...utils.log_handler import LOG_HANDLER
from ...llm.get_llm_client import get_llm_client
from .create_final_skill_challenge_prompt_handler import CreateFinalSkillChallengePromptHandler
from openai.types.completion import Completion
from termcolor import colored



class SendGenerateFinalChallengePromptToLLMHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.page = DB.get(Page, data['pageId'])
        self.topic = self.outline.topic
        self.logging = LOG_HANDLER(self.__class__.__name__)


    def handle(self):
        self.__log_event()

        # Check if course is incomplete
        if self._check_course_incomplete(self.page):
            print(colored("Course is incomplete, skipping LLM prompt generation", "yellow"))
            return None

        # Build prompt
        prompt_handler = CreateFinalSkillChallengePromptHandler(self.thread_id, self.outline, self.page)
        prompt = prompt_handler.handle()
        messages = prompt.payload

        # Send to ChatGPT
        llm_client = get_llm_client()
        completion = llm_client.send_prompt('final-skill-challenge', messages)

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


    def _check_course_incomplete(self, page: Page):
        course_pages = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == "Page",
            Page.course_id == page.course_id,
            Page.type == 'lesson',
            Page.active == True,
        ).all()

        return True in [page.content == None for page in course_pages]


    def __log_event(self):
        self.logging.info(f"Thread: {self.thread_id} - Outline: {self.outline.id} - Page: {self.page.id}")

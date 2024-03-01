from db.db import DB, Outline, Response, Page
from ...utils.log_handler import LOG_HANDLER
from ..validate_llm_response_handler import ValidateLLMResponseHandler
from termcolor import colored
from sqlalchemy.orm.attributes import flag_modified




class ProcessChallengePageResponseHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.response = DB.get(Response, data['responseId'])
        self.page = DB.get(Page, data['pageId'])
        self.prompt = self.response.prompt
        self.topic = self.outline.topic
        self.logging = LOG_HANDLER(self.__class__.__name__)


    def handle(self) -> Outline:
        self.__log_event()

        completion = self.response.payload

        validated_response = ValidateLLMResponseHandler(
            self.thread_id,
            self.outline.id,
            self.response.id
        ).handle()

        if not validated_response:
            return False
            # Retry

        self.page = self._save_content_to_page(completion)

        return self.outline


    def _save_content_to_page(self, completion: dict):
        material = completion['choices'][0]['message']['content']
        content_hash = Page.hash_content(material)

        # Update page record
        self.page.content = material
        self.page.hash = content_hash
        self.page.link = self.page.permalink
        self.page.generated = True

        # Save to Database
        DB.commit()


    def __log_event(self):
        self.logging.info(f"Thread: {self.thread_id} - Outline: {self.outline.id}")

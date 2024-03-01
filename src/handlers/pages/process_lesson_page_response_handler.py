from db.db import DB, Outline, Response, Page
from ...utils.log_handler import LOG_HANDLER
from ..validate_llm_response_handler import ValidateLLMResponseHandler
from .create_summarize_page_prompt_handler import CreateSummarizePagePromptHandler
from .send_generate_page_summary_to_llm_handler import SendGeneratePageSummaryToLLMHandler




class ProcessLessonPageResponseHandler:
    def __init__(self, thread_id: int, outline_id: int, response_id: int, page_id: int):
        self.thread_id = thread_id
        self.outline = DB.get(Outline, outline_id)
        self.response = DB.get(Response, response_id)
        self.page = DB.get(Page, page_id)
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

        self.generate_page_summary()

        return self.outline


    def generate_page_summary(self):
        response = SendGeneratePageSummaryToLLMHandler(self.thread_id, self.outline.id, self.page.id).handle()

        self.page.summary = response.content
        DB.commit()


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

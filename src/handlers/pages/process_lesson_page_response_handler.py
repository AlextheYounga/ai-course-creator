from db.db import DB, Outline, Response, Page
from ..validate_llm_response_handler import ValidateLLMResponseHandler
from .create_summarize_page_prompt_handler import CreateSummarizePagePromptHandler
from .send_generate_page_summary_to_llm_handler import SendGeneratePageSummaryToLLMHandler




class ProcessLessonPageResponseHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.response = DB.get(Response, data['responseId'])
        self.page = DB.get(Page, data['pageId'])
        self.prompt = self.response.prompt
        self.topic = self.outline.topic


    def handle(self) -> Outline:
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

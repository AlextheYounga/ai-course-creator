from db.db import DB, Outline, Response, Page
from ..validate_llm_response_handler import ValidateLLMResponseHandler
from src.events.event_manager import EVENT_MANAGER
from src.events.events import InvalidLessonPageResponseFromLLM, LessonPageResponseProcessedSuccessfully




class ProcessLessonPageResponseHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.response = DB.get(Response, data['responseId'])
        self.page = DB.get(Page, data['pageId'])
        self.prompt = self.response.prompt
        self.topic = self.outline.topic
        self.event_payload = {
            'threadId': self.thread_id,
            'outlineId': self.outline.id,
            'responseId': self.response.id,
            'topicId': self.topic.id,
            'promptId': self.prompt.id,
            **data
        }


    def handle(self) -> Outline:
        completion = self.response.payload

        validated_response = ValidateLLMResponseHandler(self.event_payload).handle()

        if not validated_response:
            if self.prompt.attempts <= 3:
                raise Exception("Invalid response; maximum retries exceeded. Aborting...")

            # Retry
            self.prompt.increment_attempts(DB)
            return EVENT_MANAGER.trigger(InvalidLessonPageResponseFromLLM(self.event_payload))

        self.page = self._save_content_to_page(completion)

        return EVENT_MANAGER.trigger(
            LessonPageResponseProcessedSuccessfully(self.event_payload)
        )


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

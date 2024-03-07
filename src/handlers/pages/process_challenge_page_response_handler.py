from db.db import DB, Outline, Response, Page
from ..validate_llm_response_handler import ValidateLLMResponseHandler
from src.events.event_manager import EVENT_MANAGER
from src.events.events import InvalidChallengePageResponseFromLLM, ChallengePageResponseProcessedSuccessfully


class ProcessChallengePageResponseHandler:
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
            return EVENT_MANAGER.trigger(InvalidChallengePageResponseFromLLM(self.event_payload))

        content = self._add_header_to_challenge_content(completion)
        self.page = self._save_content_to_page(content)

        return EVENT_MANAGER.trigger(
            ChallengePageResponseProcessedSuccessfully(self.event_payload)
        )

    def _add_header_to_challenge_content(self, completion: dict):
        content = completion['choices'][0]['message']['content']
        header = "# Practice Skill Challenge\n"

        if self.page.type == 'final-skill-challenge':
            header = "# Final Skill Challenge\n"

        # If header is h1, skip
        if content[:2] == '# ': return content

        # If header is h2, make h1
        if content[:3] == '## ':
            split_content = content.split('## ', 1)[1]
            content = '# ' + split_content

        # If header is h3, make h1
        if content[:3] == '### ':
            split_content = content.split('## ', 1)[1]
            content = '# ' + split_content

        if content[:2] != '# ':
            content = header + content

        return content

    def _save_content_to_page(self, material: str):
        content_hash = Page.hash_page(material)

        # Update page record
        self.page.content = material
        self.page.hash = content_hash
        self.page.link = self.page.permalink
        self.page.generated = True

        # Save to Database
        DB.commit()

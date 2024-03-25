from db.db import DB, Page, Outline, Prompt, Response
from src.events.event_manager import EVENT_MANAGER
from src.events.events import LessonPageSummarizedSuccessfully, InvalidPageSummaryResponseFromOpenAI
from ...llm.get_llm_client import get_llm_client
from .create_summarize_page_prompt_handler import CreateSummarizePagePromptHandler
from openai.types.completion import Completion
import json

"""
This handler is the simplest LLM handler, as it requires no real validation. The request is sent, processed
and saved from this single handler. 
"""


class GenerateLessonPageSummaryHandler():
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.page = DB.get(Page, data['pageId'])
        self.topic = self.outline.topic

    def handle(self):
        # Build prompt
        CreateSummarizePagePromptHandler(self._event_payload()).handle()

        prompt = DB.query(Prompt).filter(
            Prompt.subject == 'summarize-page'
        ).order_by(
            Prompt.id.desc()
        ).first()

        llm_client = get_llm_client()
        completion = llm_client.send_prompt(prompt)

        if completion == None:
            return EVENT_MANAGER.trigger(
                InvalidPageSummaryResponseFromOpenAI(self._event_payload(prompt))
            )

        response = self._save_response_to_db(prompt, completion)

        self._update_page_with_summary(response)

        return EVENT_MANAGER.trigger(
            LessonPageSummarizedSuccessfully(self._event_payload(prompt, response))
        )


    def _save_response_to_db(self, prompt: Prompt, completion: Completion):
        properties = {
            'params': prompt.properties['params'],
        }

        response = Response(
            thread_id=self.thread_id,
            outline_id=self.outline.id,
            prompt_id=prompt.id,
            role=completion.choices[0].message.role,
            payload=json.loads(completion.model_dump_json()),
            model=completion.model,
            prompt_tokens=completion.usage.prompt_tokens,
            completion_tokens=completion.usage.completion_tokens,
            total_tokens=completion.usage.total_tokens,
            content=completion.choices[0].message.content,
            properties=properties
        )

        DB.add(response)
        DB.commit()

        return response


    def _update_page_with_summary(self, response: Response):
        self.page.summary = response.content
        DB.commit()


    def _event_payload(self, prompt: Prompt | None = None, response: Response | None = None):
        payload = {
            'threadId': self.thread_id,
            'outlineId': self.outline.id,
            'topicId': self.topic.id,
            'pageId': self.page.id,
        }

        if prompt:
            payload['promptId'] = prompt.id
        if response:
            payload['responseId'] = response.id

        return payload

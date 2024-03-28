from db.db import DB, Page, Outline, Prompt, Response
from src.events.event_manager import EVENT_MANAGER
from src.events.events import LessonPageResponseReceivedFromOpenAI
from ...llm.get_llm_client import get_llm_client
from openai.types.completion import Completion
import json


class SendGenerateLessonPagePromptToOpenAIHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.prompt = DB.get(Prompt, data['promptId'])
        self.page = DB.get(Page, data['pageId'])
        self.topic = self.outline.topic


    def handle(self):
        llm_client = get_llm_client()
        completion = llm_client.send_prompt(self.prompt)

        response = self._save_response_to_db(completion)

        self.prompt.increment_attempts(DB)

        return EVENT_MANAGER.trigger(
            LessonPageResponseReceivedFromOpenAI({
                'threadId': self.thread_id,
                'outlineId': self.outline.id,
                'topicId': self.topic.id,
                'promptId': self.prompt.id,
                'responseId': response.id,
                'pageId': self.page.id,
            }))


    def _save_response_to_db(self, completion: Completion):
        properties = {
            'params': self.prompt.properties['params'],
        }

        response = Response(
            thread_id=self.thread_id,
            outline_id=self.outline.id,
            prompt_id=self.prompt.id,
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
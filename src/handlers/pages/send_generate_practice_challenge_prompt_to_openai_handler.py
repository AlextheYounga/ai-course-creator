from db.db import DB, Page, Outline, OutlineEntity, Prompt, Response
from src.events.event_manager import EVENT_MANAGER
from src.events.events import PracticeChallengePageResponseReceivedFromOpenAI, PracticeChallengeGenerationFailedDueToIncompleteChapter
from ...llm.get_llm_client import get_llm_client
from openai.types.completion import Completion
from termcolor import colored
import json


class SendGeneratePracticeChallengePromptToOpenAIHandler:
    def __init__(self, data: dict):
        self.data = data
        self.prompt = DB.get(Prompt, data['promptId'])
        self.page = DB.get(Page, data['pageId'])


    def handle(self):
        if self._check_if_chapter_incomplete(self.page):
            print(colored("Course is incomplete, skipping LLM prompt generation", "yellow"))
            return EVENT_MANAGER.trigger(
                PracticeChallengeGenerationFailedDueToIncompleteChapter(self._event_payload())
            )

        llm_client = get_llm_client()
        completion = llm_client.send_prompt(self.prompt)

        response = self._save_response_to_db(completion)

        self.prompt.increment_attempts(DB)

        return EVENT_MANAGER.trigger(
            PracticeChallengePageResponseReceivedFromOpenAI(self._event_payload(response))
        )


    def _save_response_to_db(self, completion: Completion):
        properties = {
            'params': self.prompt.properties['params'],
        }

        response = Response(
            thread_id=self.data['threadId'],
            outline_id=self.data['outlineId'],
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

    def _check_if_chapter_incomplete(self, page: Page):
        chapter_pages = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == "Page",
            Page.course_id == page.course_id,
            Page.chapter_id == page.chapter_id,
            Page.type == 'lesson',
            Page.active == True,
        ).all()

        return True in [page.content == None for page in chapter_pages]


    def _event_payload(self, response: Response | None = None):
        payload = self.data.copy()

        if response:
            payload['responseId'] = response.id

        return payload

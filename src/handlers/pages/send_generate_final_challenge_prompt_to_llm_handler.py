from db.db import DB, Page, Outline, OutlineEntity, Prompt, Response
from src.events.event_manager import EVENT_MANAGER
from src.events.events import FinalSkillChallengePageResponseReceivedFromLLM, FinalChallengeGenerationFailedDueToIncompleteCourse
from ...llm.get_llm_client import get_llm_client
from openai.types.completion import Completion
from termcolor import colored



class SendGenerateFinalChallengePromptToLLMHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.prompt = DB.get(Prompt, data['promptId'])
        self.page = DB.get(Page, data['pageId'])
        self.topic = self.outline.topic


    def handle(self):
        if self._check_if_course_incomplete(self.page):
            print(colored("Course is incomplete, skipping LLM prompt generation", "yellow"))
            return EVENT_MANAGER.trigger(
                FinalChallengeGenerationFailedDueToIncompleteCourse(self._event_payload())
            )

        llm_client = get_llm_client()
        completion = llm_client.send_prompt(self.prompt)

        response = self._save_response_to_db(completion)

        return EVENT_MANAGER.trigger(
            FinalSkillChallengePageResponseReceivedFromLLM(self._event_payload(response))
        )


    def _save_response_to_db(self, completion: Completion):
        properties = {
            'params': self.prompt.properties['params'],
        }

        response = Response(
            thread_id=self.thread_id,
            outline_id=self.outline.id,
            prompt_id=self.prompt.id,
            role=completion.choices[0].message.role,
            payload=completion.model_dump_json(),
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


    def _check_if_course_incomplete(self, page: Page):
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


    def _event_payload(self, response: Response | None = None):
        payload = {
            'threadId': self.thread_id,
            'outlineId': self.outline.id,
            'topicId': self.topic.id,
            'promptId': self.prompt.id,
            'pageId': self.page.id,
        }

        if response:
            payload['responseId'] = response.id

        return payload

from db.db import DB, Outline, Prompt, Page
from src.events.event_manager import EVENT_MANAGER
from src.events.events import SummarizePagePromptCreated
from ...llm import *


class CreateSummarizePagePromptHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.page = DB.get(Page, data['pageId'])
        self.topic = self.outline.topic
        self.prompt_subject = 'summarize-page'  # corresponds with key in params.yaml



    def handle(self) -> Prompt:
        llm_params = get_llm_params(self.prompt_subject)
        model = llm_params['model']

        messages = self._build_summarize_page_prompt()
        tokens = count_tokens_using_encoding(model, messages)

        prompt = self._save_prompt(messages, tokens, llm_params)

        return EVENT_MANAGER.trigger(
            SummarizePagePromptCreated({
                'threadId': self.thread_id,
                'outlineId': self.outline.id,
                'topicId': self.topic.id,
                'promptId': prompt.id,
            }))


    def _build_summarize_page_prompt(self):
        topic = self.page.topic
        summarize_prompt = get_prompt(topic, 'user/pages/summarize', {'content': self.page.content})

        return [
            {"role": "user", "content": summarize_prompt},
        ]


    def _save_prompt(self, messages: list[dict], tokens: int, params: dict) -> Prompt:
        content = messages[0]['content']

        properties = {
            'params': params,
        }

        prompt = Prompt(
            thread_id=self.thread_id,
            outline_id=self.outline.id,
            subject=self.prompt_subject,
            model=properties['params']['model'],
            content=content,
            payload=messages,
            estimated_tokens=tokens,
            properties=properties,
        )

        DB.add(prompt)
        DB.commit()

        return prompt

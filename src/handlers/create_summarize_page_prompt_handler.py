from db.db import DB, Outline, Prompt, Page
from src.events.events import SummarizePagePromptCreated
from src.utils.llm import *


class CreateSummarizePagePromptHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.outline = self.db.get(Outline, data['outlineId'])
        self.page = self.db.get(Page, data['pageId'])
        self.prompt_subject = 'summarize-page'  # corresponds with key in configs/params.yaml



    def handle(self) -> Prompt:
        llm_params = get_llm_params(self.prompt_subject)
        messages = self._build_summarize_page_prompt()
        tokens = count_token_estimate(messages)

        prompt = self._save_prompt(messages, tokens, llm_params)

        return SummarizePagePromptCreated({
            **self.data,
            'promptId': prompt.id,
        })


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
            outline_id=self.data['outlineId'],
            subject=self.prompt_subject,
            model=properties['params']['model'],
            content=content,
            payload=messages,
            estimated_tokens=tokens,
            properties=properties,
        )

        self.db.add(prompt)
        self.db.commit()

        return prompt

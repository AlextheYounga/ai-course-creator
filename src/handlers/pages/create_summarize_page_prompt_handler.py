from db.db import DB, Outline, Prompt, Page
from ...llm.get_prompt import get_prompt
from ...llm.get_llm_params import get_llm_params
from ...llm.token_counter import count_tokens_using_encoding


class CreateSummarizePagePromptHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.page = DB.get(Page, data['pageId'])
        self.topic = self.outline.topic



    def handle(self) -> Prompt:
        llm_params = get_llm_params('skills')
        model = llm_params['model']

        messages = self._build_summarize_page_prompt()
        tokens = count_tokens_using_encoding(model, messages)

        prompt = self._save_prompt(messages, tokens, llm_params)

        return prompt


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
            action=self.__class__.__name__,
            model=properties['params']['model'],
            content=content,
            payload=messages,
            estimated_tokens=tokens,
            properties=properties,
        )

        DB.add(prompt)
        DB.commit()

        return prompt
from db.db import DB, Outline, Prompt
from ...utils.log_handler import LOG_HANDLER
from ...llm.get_prompt import get_prompt
from ...llm.get_llm_params import get_llm_params
from ...llm.token_counter import count_tokens_using_encoding



class CreateGenerateSkillsPromptHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.topic = self.outline.topic
        self.logging = LOG_HANDLER(self.__class__.__name__)


    def handle(self) -> Prompt:
        self.__log_event()

        llm_params = get_llm_params('skills')
        model = llm_params['model']

        messages = self._build_skills_prompt()
        tokens = count_tokens_using_encoding(model, messages)

        prompt = self._save_prompt(messages, tokens, llm_params)

        return prompt


    def _build_skills_prompt(self) -> list[dict]:
        # Build message payload
        system_prompt = get_prompt(self.topic, 'system/general', {'topic': self.topic.name})
        user_prompt = get_prompt(self.topic, 'user/outlines/topic-skills', {'topic': self.topic.name})

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]


    def _save_prompt(self, messages: list[dict], tokens: int, params: dict) -> Prompt:
        content = ""
        for message in messages:
            content += message['content'] + "\n\n"

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


    def __log_event(self):
        self.logging.info(f"Thread: {self.thread_id} - Outline: {self.outline.id}")

from db.db import DB, Outline, Prompt
from src.events.event_manager import EVENT_MANAGER
from src.events.events import GenerateSkillsPromptCreated
from ...llm.get_prompt import get_prompt
from ...llm.get_llm_params import get_llm_params
from ...llm.token_counter import count_tokens_using_encoding



class CreateGenerateSkillsPromptHandler:
    def __init__(self, data: dict):
        self.data = data
        self.outline = DB.get(Outline, data['outlineId'])
        self.topic = self.outline.topic
        self.prompt_subject = 'skills'  # corresponds with key in configs/params.yaml


    def handle(self) -> GenerateSkillsPromptCreated:
        llm_params = get_llm_params(self.prompt_subject)
        model = llm_params['model']

        messages = self._build_skills_prompt()
        tokens = count_tokens_using_encoding(model, messages)

        prompt = self._save_prompt(messages, tokens, llm_params)

        return EVENT_MANAGER.trigger(
            GenerateSkillsPromptCreated({
                **self.data,
                'promptId': prompt.id,
            }))


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
            thread_id=self.data['threadId'],
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

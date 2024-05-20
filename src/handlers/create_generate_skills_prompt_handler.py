from db.db import DB, Topic, Outline, Prompt
from src.events.events import GenerateSkillsPromptCreated
from ..utils.llm.get_prompt import get_prompt
from ..utils.llm.get_llm_params import get_llm_params
from ..utils.llm.token_counter import count_token_estimate



class CreateGenerateSkillsPromptHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.outline = self.db.get(Outline, data['outlineId'])
        self.topic = self.db.get(Topic, data['topicId'])
        self.prompt_subject = 'skills'  # corresponds with key in configs/params.yaml


    def handle(self) -> GenerateSkillsPromptCreated:
        llm_params = get_llm_params(self.prompt_subject)
        messages = self._build_skills_prompt()
        tokens = count_token_estimate(messages)

        prompt = self._save_prompt(messages, tokens, llm_params)

        return GenerateSkillsPromptCreated({
            **self.data,
            'promptId': prompt.id,
        })


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
            outline_id=self.outline.id,
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

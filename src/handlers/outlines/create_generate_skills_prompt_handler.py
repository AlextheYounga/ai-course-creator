from db.db import DB, Outline, Thread, Prompt
from ...llm.get_prompt import get_prompt
from ...utils.log_handler import LOG_HANDLER
from ...llm.get_llm_params import get_llm_params
from ...llm.token_counter import count_tokens_using_encoding
from termcolor import colored



class CreateGenerateSkillsPromptHandler:
    def __init__(self, thread_id: int, outline_id: int):
        self.thread = DB.get(Thread, thread_id)
        self.outline = DB.get(Outline, outline_id)
        self.topic = self.outline.topic
        self.logger = LOG_HANDLER.getLogger(self.__class__.__name__)


    def handle(self):
        print(colored(f"\nGenerating {self.topic.name} skills...", "yellow"))
        llm_params = get_llm_params('skills')
        model = llm_params['model']

        properties = {
            'params': llm_params,
        }

        messages = self._build_skills_prompt()
        tokens = count_tokens_using_encoding(model, messages)

        prompt = self._save_prompt('generate-skills', messages, tokens, properties)

        return prompt


    def _build_skills_prompt(self) -> list[dict]:
        # Build message payload
        system_prompt = get_prompt(self.topic, 'system/general', {'topic': self.topic.name})
        user_prompt = get_prompt(self.topic, 'user/outlines/topic-skills', {'topic': self.topic.name})

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def _save_prompt(self, event_name: str, messages: list[dict], tokens: int, properties: dict) -> int:
        content = ""
        for message in messages:
            content += message['content'] + "\n\n"

        prompt = Prompt(
            action=event_name,
            model=properties['model'],
            content=content,
            payload=messages,
            estimated_tokens=tokens,
            properties=properties,
        )

        DB.add(prompt)
        DB.commit()

        return prompt

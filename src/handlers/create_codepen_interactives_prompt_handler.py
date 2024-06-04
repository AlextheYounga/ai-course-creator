from db.db import DB, Topic, OutlineEntity, Interactive, Prompt, Page
from src.events.events import CodepenInteractivesPromptCreated
from src.utils.llm import *


class CreateCodepenInteractivesPromptHandler:
    """
    Ideally we want to generate only one codepen interactive at a time, so if this handler is called, we are only 
    generating one codepen and we can call this handler again from the CalculateInteractiveCountsForPageHandler if need be.
    """

    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.topic = self.db.get(Topic, data['topicId'])
        self.page = self.db.get(Page, data['pageId'])
        self.interactive_type = 'codepen'
        self.next_events = []
        self.generate_count = '2'  # Generate maximum of 2 codepens per prompt


    def handle(self) -> Prompt:
        llm_params = get_llm_params(self.interactive_type)
        messages = self._build_codepen_interactive_prompt()
        tokens = count_token_estimate(messages)

        prompt = self._save_prompt(messages, tokens, llm_params)

        return CodepenInteractivesPromptCreated({
            **self.data,
            'promptId': prompt.id,
        })


    def _build_codepen_interactive_prompt(self):
        general_system_prompt = get_prompt(self.topic, 'system/general', {'topic': self.topic.name})
        interactive_shape_prompt = get_prompt(self.topic, f"system/interactives/{self.interactive_type}")
        interactive_context_prompt = self._get_interactive_context_system_prompt()

        system_prompt = "\n".join([
            general_system_prompt,
            interactive_shape_prompt,
            interactive_context_prompt
        ])

        # We will only generate one of these per prompt for maximum quality
        count_of_type = f"{self.generate_count} {self.interactive_type} shortcode blocks"
        user_prompt = get_prompt(self.topic, 'user/interactives', {'count_of_type': count_of_type})

        # Build message payload
        system_payload = [{"role": "system", "content": system_prompt}]
        user_payload = [{"role": "user", "content": user_prompt}]

        return system_payload + user_payload


    def _get_interactive_context_system_prompt(self):
        outline_interactives = self.db.query(Interactive).join(
            OutlineEntity, Interactive.outline_entity_id == OutlineEntity.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
        ).all()

        interactive_questions = [i.get_data('question') for i in outline_interactives if i.get_data('question')]
        interactive_questions_string = '\n - '.join(interactive_questions) if interactive_questions else "No questions generated yet."

        return get_prompt(self.topic, 'system/interactive-context', {
            'content': self.page.content,
            'questions': interactive_questions_string
        })


    def _save_prompt(self, messages: list[dict], tokens: int, params: dict) -> Prompt:
        content = ""
        for message in messages:
            content += message['content'] + "\n\n"

        properties = {
            'params': params,
        }

        prompt = Prompt(
            outline_id=self.data['outlineId'],
            subject=self.interactive_type,
            model=properties['params']['model'],
            content=content,
            payload=messages,
            estimated_tokens=tokens,
            properties=properties,
        )

        self.db.add(prompt)
        self.db.commit()

        return prompt

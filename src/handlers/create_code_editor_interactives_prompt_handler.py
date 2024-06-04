from db.db import DB, Topic, OutlineEntity, Interactive, Prompt, Page
from src.events.events import CodeEditorInteractivesPromptCreated
from src.utils.llm import *


class CreateCodeEditorInteractivesPromptHandler:
    """
    Ideally we want to generate only one code editor at a time, so if this handler is called, we are only 
    generating one code editor and we can call this handler again from the CalculateInteractiveCountsForPageHandler if need be.
    """

    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.topic = self.db.get(Topic, data['topicId'])
        self.page = self.db.get(Page, data['pageId'])
        self.interactive_type = 'codeEditor'
        self.prompt_subject = 'code-editor'  # corresponds with key in configs/params.yaml
        self.generate_count = '2'  # Generate maximum of 2 code editors per prompt


    def handle(self) -> Prompt:
        llm_params = get_llm_params(self.prompt_subject)
        messages = self._build_code_editor_interactive_prompt()
        tokens = count_token_estimate(messages)

        prompt = self._save_prompt(messages, tokens, llm_params)

        return CodeEditorInteractivesPromptCreated({
            **self.data,
            'promptId': prompt.id,
        })


    def _build_code_editor_interactive_prompt(self):
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

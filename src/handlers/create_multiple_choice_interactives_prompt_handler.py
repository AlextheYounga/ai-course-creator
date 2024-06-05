from db.db import DB, Topic, OutlineEntity, Interactive, Prompt, Page
from src.events.events import MultipleChoiceInteractivesPromptCreated
from src.utils.llm import *


class CreateMultipleChoiceInteractivesPromptHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.topic = self.db.get(Topic, data['topicId'])
        self.page = self.db.get(Page, data['pageId'])
        self.interactive_type = 'multipleChoice'
        self.prompt_subject = 'multiple-choice'  # corresponds with key in configs/params.yaml


    def handle(self) -> Prompt:
        llm_params = get_llm_params(self.prompt_subject)
        messages = self._build_multiple_choice_interactives_prompt()
        tokens = count_token_estimate(messages)

        prompt = self._save_prompt(messages, tokens, llm_params)

        return MultipleChoiceInteractivesPromptCreated({
            **self.data,
            'promptId': prompt.id,
        })


    def _build_multiple_choice_interactives_prompt(self):
        general_system_prompt = get_prompt(self.topic, 'system/general', {'topic': self.topic.name})
        interactive_shape_prompt = get_prompt(self.topic, f"system/interactives/{self.interactive_type}")
        interactive_context_prompt = self._get_interactive_context_system_prompt()

        system_prompt = "\n".join([
            general_system_prompt,
            interactive_shape_prompt,
            interactive_context_prompt
        ])

        # Get count of interactives and pluralize if necessary
        # We will inject this string into the main user prompt
        multiple_choice_count = self.data['interactives'][self.interactive_type]
        count_of_type = f"{multiple_choice_count} {self.interactive_type} shortcode{'s' if multiple_choice_count > 1 else ''}"
        user_prompt = get_prompt(self.topic, 'user/interactives', {'count_of_type': count_of_type})

        # Build message payload
        system_payload = [{"role": "system", "content": system_prompt}]
        user_payload = [{"role": "user", "content": user_prompt}]

        return system_payload + user_payload


    def _get_interactive_context_system_prompt(self):
        course_pages = self.db.query(OutlineEntity, Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
            Page.course_id == self.page.course_id
        ).all()

        outline_interactives = self.db.query(Interactive).join(
            OutlineEntity, Interactive.outline_entity_id == OutlineEntity.id
        ).filter(OutlineEntity.outline_id == self.data['outlineId']).all()

        course_page_outline_entity_ids = [i[0].id for i in course_pages]
        course_interactives = [i for i in outline_interactives if i.outline_entity_id in course_page_outline_entity_ids]

        interactive_questions_string = "No questions generated yet."
        interactive_questions = [i.get_data('question') for i in course_interactives if i.get_data('question')]

        if len(interactive_questions) > 0:
            unique_interactive_questions = list(set(interactive_questions))  # We need to save as many tokens as possible
            interactive_questions_string = '\n - '.join(unique_interactive_questions)

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

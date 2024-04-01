from db.db import DB, Topic, OutlineEntity, Prompt, Page
from src.events.event_manager import EVENT_MANAGER
from src.events.events import FinalSkillChallengePagePromptCreated
from ...llm import *



class CreateFinalSkillChallengePromptHandler:
    def __init__(self, data: dict):
        self.data = data
        self.topic = DB.get(Topic, data['topicId'])
        self.page = DB.get(Page, data['pageId'])
        self.prompt_subject = 'final-skill-challenge'  # corresponds with key in params.yaml


    def handle(self) -> Prompt:
        llm_params = get_llm_params(self.prompt_subject)
        model = llm_params['model']

        messages = self._build_final_skill_challenge_prompt()
        tokens = count_tokens_using_encoding(model, messages)

        prompt = self._save_prompt(messages, tokens, llm_params)

        return EVENT_MANAGER.trigger(
            FinalSkillChallengePagePromptCreated({
                **self.data,
                'promptId': prompt.id,
            }))


    def _build_final_skill_challenge_prompt(self):
        # Combine all page content into a single string
        all_pages_content = self._prepare_course_content_prompt()
        general_system_prompt = get_prompt(self.topic, 'system/general', {'topic': self.topic.name})

        interactives_instruction_prompt = self._prepare_interactives_instruction_prompt()
        interactive_shapes_prompt = self._get_interactive_component_shape_prompts()

        combined_system_prompt = "\n".join([
            general_system_prompt,
            interactives_instruction_prompt,
            interactive_shapes_prompt,
            all_pages_content
        ])

        user_prompt = get_prompt(self.topic, 'user/challenges/final-skill-challenge')

        # Build message payload
        system_payload = [{"role": "system", "content": combined_system_prompt}]
        user_payload = [{"role": "user", "content": user_prompt}]

        return system_payload + user_payload


    def _prepare_interactives_instruction_prompt(self):
        interactives_list = '\n'
        topic_interactives = self._get_interactives_settings()
        available_interactives = {
            'codeEditor': 'Code Editor',
            'multipleChoice': 'Multiple Choice',
            'fillBlank': 'Fill in the Blank',
            'trueFalse': 'True/False',
            'codepen': 'CodePen'
        }

        for interactive in available_interactives:
            if topic_interactives.get(interactive, True):
                interactives_list += f"- {interactive}\n"

        interactives_list += '\n'

        return get_prompt(
            self.topic,
            'system/tune-interactives',
            {'interactives': interactives_list}
        )


    def _get_interactive_component_shape_prompts(self):
        interactives = []
        topic_interactives = self._get_interactives_settings()
        available_interactives = ['codeEditor', 'multipleChoice', 'fillBlank', 'trueFalse', 'codepen']

        for interactive in available_interactives:
            if topic_interactives.get(interactive, True):
                prompt = get_prompt(self.topic, f"system/interactives/{interactive}")
                interactives.append(prompt)

        return "\n\n".join(interactives)


    def _prepare_course_content_prompt(self):
        # Combine all page content into a single string
        course_pages_content = "The following is all the content from this course:\n\n"

        # Fetch all course pages
        pages = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == "Page",
            Page.course_id == self.page.course_id,
            Page.type == 'lesson',
            Page.active == True,
        ).all()

        for page in pages:
            course_pages_content += f"{page.content}\n\n"

        return course_pages_content


    def _save_prompt(self, messages: list[dict], tokens: int, params: dict) -> Prompt:
        content = ""
        for message in messages:
            content += message['content'] + "\n\n"

        properties = {
            'params': params,
        }

        prompt = Prompt(
            thread_id=self.data['threadId'],
            outline_id=self.data['outlineId'],
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

    def _get_interactives_settings(self):
        scoped_settings = self.topic.get_settings('final-skill-challenge')
        topic_interactives = scoped_settings.get("interactives", {})

        return topic_interactives

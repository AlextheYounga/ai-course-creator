from db.db import DB, Outline, OutlineEntity, Prompt, Page
from ...llm.get_prompt import get_prompt
from ...llm.get_llm_params import get_llm_params
from ...llm.token_counter import count_tokens_using_encoding



class CreateFinalSkillChallengePromptHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.page = DB.get(Page, data['pageId'])
        self.topic = self.outline.topic



    def handle(self) -> Prompt:
        llm_params = get_llm_params('skills')
        model = llm_params['model']

        messages = self._build_final_skill_challenge_prompt()
        tokens = count_tokens_using_encoding(model, messages)

        prompt = self._save_prompt(messages, tokens, llm_params)

        return prompt


    def _build_final_skill_challenge_prompt(self):
        topic_language = self.topic.properties.get("language", self.topic.slug)

        # Combine all page content into a single string
        all_pages_content = self._prepare_course_content_prompt()
        general_system_prompt = get_prompt(self.topic, 'system/general', {'topic': self.topic.name})
        interactives_system_prompt = get_prompt(self.topic, 'system/tune-interactives', {'topicLanguage': topic_language})

        combined_system_prompt = "\n".join([
            general_system_prompt,
            interactives_system_prompt,
            all_pages_content
        ])

        user_prompt = get_prompt(self.topic, 'user/challenges/final-skill-challenge')

        # Build message payload
        system_payload = [{"role": "system", "content": combined_system_prompt}]
        user_payload = [{"role": "user", "content": user_prompt}]

        return system_payload + user_payload


    def _prepare_course_content_prompt(self):
        # Combine all page content into a single string
        course_pages_content = "The following is all the content from this course:\n\n"

        # Fetch all course pages
        pages = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
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

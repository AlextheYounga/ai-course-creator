from ...utils.prompts import get_prompt
from db.db import DB, Page, Outline, OutlineEntity


class BuildPracticeChallengePromptHandler:
    def __init__(self, outline: Outline, page: Page):
        self.topic = outline.topic
        self.outline = outline
        self.page = page

    def handle(self):
        topic_language = self.topic.properties.get("language", self.topic.slug)

        # Combine all page content into a single string
        all_pages_content = self._prepare_chapter_content_prompt()
        general_system_prompt = get_prompt(self.topic, 'system/general', {'topic': self.topic.name})
        interactives_system_prompt = get_prompt(self.topic, 'system/tune-interactives', {'topicLanguage': topic_language})

        combined_system_prompt = "\n".join([
            general_system_prompt,
            interactives_system_prompt,
            all_pages_content
        ])

        user_prompt = get_prompt(self.topic, 'user/challenges/practice-skill-challenge')

        # Build message payload
        system_payload = [{"role": "system", "content": combined_system_prompt}]
        user_payload = [{"role": "user", "content": user_prompt}]

        return system_payload + user_payload


    def _prepare_chapter_content_prompt(self):
        # Combine all page content into a single string
        chapter_pages_content = "The following is all the content from this chapter:\n\n"

        # Fetch all chapter pages
        chapter_pages = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == "Page",
            Page.course_id == self.page.course_id,
            Page.chapter_id == self.page.chapter_id,
            Page.type == 'lesson',
            Page.active == True,
        ).all()

        for page in chapter_pages:
            if page.content != None:
                chapter_pages_content += f"{page.content}\n\n"

        return chapter_pages_content

from helpers import get_prompt
from db.db import DB, Page, Outline, OutlineEntity
import yaml


class BuildLessonPagePromptHandler:
    def __init__(self, outline: Outline, page: Page):
        self.topic = outline.topic
        self.outline = outline
        self.page = page


    def handle(self):
        topic_language = self.topic.properties.get("language", self.topic.slug)

        # Combine multiple system prompts into one
        general_system_prompt = get_prompt(self.topic, 'system/general', {'topic': self.topic.name})

        # Inform model on how we want to format interactives
        interactives_system_prompt = get_prompt(self.topic, 'system/tune-interactives', {'topicLanguage': topic_language})

        # Inform model on our outline
        pruned_outline = self._prune_challenges_from_outline()
        material_system_prompt = get_prompt(self.topic, 'system/pages/tune-outline', {
            'topic': self.topic.name,
            'outline': yaml.dump(pruned_outline, sort_keys=False)
        })

        # Get prior page summaries
        summaries = self._collect_prior_page_summaries()

        prior_page_material_prompt = get_prompt(self.topic, 'system/pages/tune-page-summaries', {
            'summaries': summaries
        })

        combined_system_prompt = "\n---\n".join([
            general_system_prompt,
            interactives_system_prompt,
            material_system_prompt,
            prior_page_material_prompt
        ])

        user_prompt = get_prompt(self.topic, 'user/pages/page-material', {'page_name': self.page.name})

        # Build message payload
        return [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": user_prompt}
        ]


    def _collect_prior_page_summaries(self):
        summaries = ""

        # Fetch all pages from outline
        lesson_pages = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == "Page",
            Page.type == 'page',
            Page.active == True,
        ).all()

        for page in lesson_pages:
            if page.summary != None:
                formatted_summary = page.summary.replace("\n", " ")
                summaries += f"## {page.name}\n {formatted_summary}\n\n"

        return summaries


    def _prune_challenges_from_outline(self):
        outline_formatted = []

        for course in self.outline.master_outline:
            course_object = {
                'course': {
                    'courseName': course['course']['courseName'],
                    'chapters': []
                }
            }

            chapters = course['course']['chapters']
            pruned_chapters = [chapter for chapter in chapters if chapter['name'] != 'Final Skill Challenge']
            course_object['course']['chapters'] = pruned_chapters

            for index, chapter in enumerate(course_object['course']['chapters']):
                pages = chapter['pages']
                pruned_pages = [page for page in pages if page != 'Practice Skill Challenge']
                course_object['course']['chapters'][index]['pages'] = pruned_pages

            outline_formatted.append(course_object)
        return outline_formatted

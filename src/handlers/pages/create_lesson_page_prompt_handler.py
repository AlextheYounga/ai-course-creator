import yaml
from db.db import DB, Outline, OutlineEntity, Prompt, Page
from src.events.event_manager import EVENT_MANAGER
from src.events.events import LessonPagePromptCreated
from ...llm import *


class CreateLessonPagePromptHandler:
    def __init__(self, data: dict):
        self.data = data
        self.outline = DB.get(Outline, data['outlineId'])
        self.page = DB.get(Page, data['pageId'])
        self.topic = self.outline.topic
        self.prompt_subject = 'page-material'  # corresponds with key in configs/params.yaml


    def handle(self) -> Prompt:
        llm_params = get_llm_params(self.prompt_subject)
        model = llm_params['model']

        messages = self._build_lesson_page_prompt()
        tokens = count_tokens_using_encoding(model, messages)

        prompt = self._save_prompt(messages, tokens, llm_params)

        return EVENT_MANAGER.trigger(
            LessonPagePromptCreated({
                **self.data,
                'promptId': prompt.id,
            }))


    def _build_lesson_page_prompt(self):
        # Combine multiple system prompts into one
        general_system_prompt = get_prompt(self.topic, 'system/general', {'topic': self.topic.name})

        # Inform model on how we want to format interactives
        interactives_instruction_prompt = self._prepare_interactives_instruction_prompt()
        interactive_shapes_prompt = self._get_interactive_component_shape_prompts()

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
        }) if len(summaries) > 0 else ""

        combined_system_prompt = "\n---\n".join([
            general_system_prompt,
            interactives_instruction_prompt,
            interactive_shapes_prompt,
            material_system_prompt,
            prior_page_material_prompt
        ])

        user_prompt = get_prompt(self.topic, 'user/pages/page-material', {'page_name': self.page.name})

        # Build message payload
        return [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": user_prompt}
        ]


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

    def _collect_prior_page_summaries(self):
        summaries = ""

        # Fetch all pages from outline
        lesson_pages = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == "Page",
            Page.type == 'lesson',
            Page.active == True,
        ).all()

        for page in lesson_pages:
            if page.summary != None:
                formatted_summary = page.summary.replace("\n", " ")
                summaries += f"## {page.name}\n {formatted_summary}\n\n"

        return summaries


    def _prune_challenges_from_outline(self):
        outline_formatted = []

        for course in self.outline.outline_data:
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


    def _get_interactives_settings(self):
        scoped_settings = self.topic.get_settings('lesson')
        topic_interactives = scoped_settings.get("interactives", {})

        return topic_interactives

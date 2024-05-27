from db.db import DB, OutlineEntity, Topic, Page, Interactive
from src.events.events import CompiledInteractivesToLessonPage


class CompileInteractivesToLessonPageHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.page = self.db.get(Page, data['pageId'])
        self.topic = self.db.get(Topic, data['topicId'])


    def handle(self):
        lesson_interactives_count = self._get_topic_interactive_count_settings()
        page_outline_entity_id = self._get_page_outline_entity_id()

        codepen_interactives = self.db.query(Interactive).filter(
            Interactive.type == 'codepen',
            Interactive.outline_entity_id == page_outline_entity_id
        ).all()

        selectedInteractives = []

        # If there are codepen interactives, prioritize those over anything else for lesson pages.
        if len(codepen_interactives) > 0:
            selectedInteractives = codepen_interactives[:lesson_interactives_count]
        else:
            # Else we'll get the first interactives for this page.
            lessonInteractives = self.db.query(Interactive).filter(
                Interactive.outline_entity_id == page_outline_entity_id
            ).all()

            selectedInteractives = lessonInteractives[:lesson_interactives_count]

        self.page.interactive_ids = [i.id for i in selectedInteractives]
        self.db.commit()

        self.page.update_properties(self.db, {
            'interactives': self._compile_page_interactive_shortcodes(self.page.interactive_ids)
        })

        return CompiledInteractivesToLessonPage(self.data)


    def _compile_page_interactive_shortcodes(self, interactive_ids: list[int]):
        content = []

        selected_interactives = self.db.query(Interactive).filter(
            Interactive.id.in_(interactive_ids)
        ).order_by(Interactive.difficulty).all()

        for interactive in selected_interactives:
            content.append(interactive.get_data('shortcode'))

        return "\n\n".join(content)


    def _get_page_outline_entity_id(self):
        return self.db.query(OutlineEntity).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
            OutlineEntity.entity_id == self.page.id
        ).first().id


    def _get_topic_interactive_count_settings(self):
        topic_settings = self.topic.get_properties('settings')
        interactive_options = topic_settings.get('interactives', {})
        interactives_counts = interactive_options.get('counts', {
            'lesson': 1,
            'challenge': 5,
            'final-skill-challenge': 20
        })

        return interactives_counts['lesson']

from functools import lru_cache
from db.db import DB, Topic, Page, Interactive, PageInteractive, OutlineEntity
from src.events.events import CompiledInteractivesToLessonPages


class CompileInteractivesToLessonPagesHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.page_ids = data.get('generationIds', None)
        self.topic = self.db.get(Topic, data['topicId'])
        self.next_events = []

    def handle(self):
        lesson_pages = self.get_lesson_pages()
        lesson_interactives_count = self._get_topic_interactive_count_settings()['lesson']
        already_associated_interactive_ids = [i[0] for i in self.db.query(PageInteractive.interactive_id).all()]

        for page in lesson_pages:
            selected_interactives = []
            page_interactives = self._get_interactives_generated_from_page(page)
            if len(page_interactives) < lesson_interactives_count: continue
            remaining_interactives = [i for i in page_interactives if i.id not in already_associated_interactive_ids]
            codepen_interactives = [i for i in remaining_interactives if i.type == 'codepen']

            if len(codepen_interactives) > 0:
                selected_interactives = codepen_interactives[:lesson_interactives_count]
            else:
                selected_interactives = remaining_interactives[:lesson_interactives_count]

            # Save to DB
            for interactive in selected_interactives:
                page_interactive = PageInteractive(
                    interactive_id=interactive.id,
                    page_id=page.id
                )
                self.db.add(page_interactive)
                already_associated_interactive_ids.append(interactive.id)
            self.db.commit()


        return CompiledInteractivesToLessonPages(self.data)


    def _get_interactives_generated_from_page(self, page: Page):
        return self.db.query(Interactive).filter(
            Interactive.page_source_id == page.id
        ).all()


    @ lru_cache(maxsize=None)  # memoize
    def _get_topic_interactive_count_settings(self):
        topic_settings = self.topic.get_properties('settings')
        interactive_options = topic_settings.get('interactives', {})
        interactives_counts = interactive_options.get('counts', {
            'lesson': 1,
            'challenge': 5,
            'final-skill-challenge': 20
        })

        return interactives_counts


    @ lru_cache(maxsize=None)  # memoize
    def get_lesson_pages(self):
        return self.db.query(Page).filter(
            Page.id.in_(self.page_ids),
            Page.type == 'lesson'
        ).all()

from functools import lru_cache
from db.db import DB, Topic, Page, Interactive, PageInteractive, OutlineEntity
from src.events.events import CompiledInteractivesToLessonPages


class CompileInteractivesToLessonPagesHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.page_ids = data.get('pageIds', None)
        self.topic = self.db.get(Topic, data['topicId'])
        self.next_events = []

    def handle(self):
        lesson_pages = self._get_lesson_pages()
        lesson_interactives_count = self._get_topic_interactive_count_settings()['lesson']
        already_associated_interactives = self.db.query(PageInteractive).all()

        for page in lesson_pages:
            selected_interactives = []
            page_interactives = self._get_interactives_generated_from_page(page)

            already_associated_interactive_ids = [i.interactive_id for i in already_associated_interactives]
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
    def _get_lesson_pages(self):
        if self.page_ids:
            return self.db.query(Page).filter(
                Page.id.in_(self.page_ids)
            ).all()

        return self.db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
            Page.type == 'lesson',
        ).all()


    # def _check_if_enough_interactives_to_compile_challenge_page(self):
    #     interactives_counts = self._get_topic_interactive_count_settings()
    #     chapter_pages = self.db.query(Page).filter(
    #         Page.chapter_id == self.page.chapter_id
    #     ).all()
    #     chapter_page_ids = [page.id for page in chapter_pages]
    #     chapter_interactives = self.db.query(Interactive).filter(
    #         Interactive.page_source_id.in_(chapter_page_ids)
    #     ).all()
    #     already_associated_chapter_interactives = self.db.query(PageInteractive).filter(
    #         PageInteractive.page_id.in_(chapter_page_ids)
    #     ).all()

    #     remaining_interactives = [i for i in chapter_interactives
    #                               if i.id not in already_associated_chapter_interactives]

    #     return len(remaining_interactives) >= interactives_counts['challenge']

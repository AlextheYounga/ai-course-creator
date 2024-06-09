from db.db import DB, OutlineEntity, Chapter, Page, PageInteractive, Interactive
from src.events.events import CollectedAllPagesForInteractiveGeneration


class CollectAllPagesForInteractiveGenerationHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.outline_entity = self.db.get(OutlineEntity, data['outlineEntityId']) if data.get('outlineEntityId', False) else False


    def handle(self):
        interactive_page_ids = []
        generation_type = self._get_outline_generation_type()
        if self.data.get('generationIds', False):
            interactive_page_ids = self.data['generationIds']
        else:
            interactive_pages_to_generate = []
            match generation_type:
                case 'FULL_OUTLINE':
                    interactive_pages_to_generate = self._get_outline_pages()
                case 'OUTLINE_ENTITY':
                    interactive_pages_to_generate = self._get_entity_pages()

            interactive_page_ids = [page.id for page in interactive_pages_to_generate]


        self._prepare_existing_page_interactive_associations_for_regeneration(interactive_page_ids)

        return CollectedAllPagesForInteractiveGeneration({
            **self.data,
            'generationType': generation_type,
            'generationIds': interactive_page_ids,
        })


    def _get_outline_generation_type(self):
        if self.outline_entity:
            return 'OUTLINE_ENTITY'

        return 'FULL_OUTLINE'


    def _get_outline_pages(self) -> list[Page]:
        return self.db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
            Page.type == 'lesson',
        ).all()


    def _get_entity_pages(self) -> list[Page]:
        if self.outline_entity.entity_type == 'Page':
            return self.db.query(Page).filter(Page.id == self.outline_entity.entity_id).all()

        query = self.db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
            Page.type == 'lesson',
        )

        if self.outline_entity.entity_type == 'Course':
            query = query.filter(
                Page.course_id == self.outline_entity.entity_id,
            )

        if self.outline_entity.entity_type == 'Chapter':
            chapter_record = self.db.get(Chapter, self.outline_entity.entity_id)

            query = query.filter(
                Page.course_id == chapter_record.course_id,
                Page.chapter_id == chapter_record.id,
            )

        return query.all()


    def _prepare_existing_page_interactive_associations_for_regeneration(self, interactive_page_ids: list[int]):
        # We will just nuke the existing page_interactives and interactives
        # We can always rebuild these from the response table
        page_interactives = self.db.query(PageInteractive).filter(
            PageInteractive.page_id.in_(interactive_page_ids)
        ).all()

        for page_interactive in page_interactives:
            interactive = self.db.get(Interactive, page_interactive.interactive_id)

            self.db.delete(page_interactive)
            self.db.delete(interactive)

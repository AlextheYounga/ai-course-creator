from db.db import DB, OutlineEntity, Chapter, Page
from src.events.events import CollectedAllPagesToGenerate


class CollectAllPagesToGenerateHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.outline_entity = self.db.get(OutlineEntity, data['outlineEntityId']) if data.get('outlineEntityId', False) else False


    def handle(self):
        pages_to_generate_ids = []
        generation_type = self._get_outline_generation_type()
        if self.data.get('generationIds', False):
            pages_to_generate_ids = self.data['generationIds']
        else:
            pages_to_generate = []
            match generation_type:
                case 'FULL_OUTLINE':
                    pages_to_generate = self._get_outline_pages()
                case 'OUTLINE_ENTITY':
                    pages_to_generate = self._get_entity_pages()

            self._prepare_already_generated_pages_for_regeneration(pages_to_generate)

            pages_to_generate_ids = [page.id for page in pages_to_generate]

        return CollectedAllPagesToGenerate({
            **self.data,
            'generationType': generation_type,
            'generationIds': pages_to_generate_ids,
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


    def _prepare_already_generated_pages_for_regeneration(self, pages_to_generate: list[Page]):
        for page in pages_to_generate:
            # Update page record
            page.content = None
            page.hash = None
            page.generated = False

            self.db.commit()

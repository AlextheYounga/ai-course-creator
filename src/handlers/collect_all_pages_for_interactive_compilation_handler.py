from db.db import DB, OutlineEntity, Page, PageInteractive
from src.events.events import CollectedAllPagesForInteractiveCompilation


class CollectAllPagesForInteractiveCompilationHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()


    def handle(self):
        all_outline_pages = self._get_outline_pages()
        all_outline_page_ids = [page.id for page in all_outline_pages]

        self._reset_existing_associations(all_outline_page_ids)

        return CollectedAllPagesForInteractiveCompilation({
            **self.data,
            'generationIds': all_outline_page_ids,
        })

    def _get_outline_pages(self) -> list[Page]:
        return self.db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
        ).all()


    def _reset_existing_associations(self, all_outline_page_ids: list[int]):
        # We will just nuke the existing page_interactives associations
        page_interactives_count = self.db.query(PageInteractive).filter(
            PageInteractive.page_id.in_(all_outline_page_ids)
        ).count()

        if page_interactives_count > 0:
            self.db.query(PageInteractive).filter(
                PageInteractive.page_id.in_(all_outline_page_ids)
            ).delete()
        self.db.commit()

from functools import lru_cache
import collections
from db.db import DB, OutlineEntity, Page, Interactive
from src.events.events import GeneratePageInterativesProcessStarted, AllInteractivesGeneratedFromPages


class GetNextPageForInteractivesGenerationHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.outline_entity = self.db.get(OutlineEntity, data['outlineEntityId']) if data.get('outlineEntityId', False) else False
        self.page_ids = data['generationIds']


    def handle(self):
        generated_page_ids = self._get_completed_interactive_page_ids()
        all_pages_generated = collections.Counter(generated_page_ids) == collections.Counter(self.page_ids)
        remaining_page_ids = list(set(self.page_ids) - set(generated_page_ids))

        if all_pages_generated:
            return AllInteractivesGeneratedFromPages(self.data)

        next_page_to_generate_id = remaining_page_ids[0]

        return GeneratePageInterativesProcessStarted(data={
            **self.data,
            'pageId': next_page_to_generate_id,
            'completedGenerationIds': generated_page_ids
        })


    @lru_cache(maxsize=None)
    def _get_pages_to_generate(self):
        return self.db.query(Page).filter(
            Page.id.in_(self.data['generationIds']),
        ).all()


    def _get_completed_interactive_page_ids(self):
        generated_interactive_page_ids = []
        pages_to_generate = self._get_pages_to_generate()

        for page in pages_to_generate:
            # If no interactivesCount, we know it hasn't been generated yet
            total_page_interactives_count = page.get_properties('interactivesCount')
            if not total_page_interactives_count: continue

            generated_page_interactives_count = self.db.query(Interactive).filter(
                Interactive.page_source_id == page.id
            ).count()

            if generated_page_interactives_count >= total_page_interactives_count:
                generated_interactive_page_ids.append(page.id)

        return generated_interactive_page_ids

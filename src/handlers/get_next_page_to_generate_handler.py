import collections
from db.db import DB, Topic, OutlineEntity, Page
from src.events.events import GenerateLessonPageProcessStarted, GenerateOutlinePagesJobFinished


class GetNextPageToGenerateHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.topic = self.db.get(Topic, data['topicId'])
        self.outline_entity = self.db.get(OutlineEntity, data['outlineEntityId']) if data.get('outlineEntityId', False) else False
        self.page_ids = data['generationIds']
        self.next_events = []


    def handle(self):
        generated_page_ids = self._get_page_ids_already_generated()
        all_pages_generated = collections.Counter(generated_page_ids) == collections.Counter(self.page_ids)
        remaining_page_ids = list(set(self.page_ids) - set(generated_page_ids))

        if all_pages_generated:
            return GenerateOutlinePagesJobFinished(self.data)


        next_page_to_generate_id = remaining_page_ids[0]

        return GenerateLessonPageProcessStarted(data={
            **self.data,
            'pageId': next_page_to_generate_id,
            'completedGenerationIds': generated_page_ids
        })


    def _get_page_ids_already_generated(self):
        generated_pages = self.db.query(Page).filter(
            Page.id.in_(self.data['generationIds']),
            Page.generated == True
        ).all()

        return [page.id for page in generated_pages]

import collections
from db.db import DB, OutlineEntity, Chapter, Page, EventStore, JobStore
from src.events.events import GenerateLessonPageProcessStarted, GenerateOutlinePagesJobFinished


class GetNextPageToGenerateFromJobHandler:
    """
    This handler is doing a lot! (which is not good practice)

    It is responsible for handling fetching the next page from both 
    full outline generation and outline entity generation. It checks if all pages all pages have 
    been generated and if not, triggering the next page generation event.

    If an outline entity id is present, it will fetch the pages associated with that entity.
    """

    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.job = self.db.query(JobStore).filter(JobStore.job_id == data['jobId']).first()
        self.outline_entity = self.db.get(OutlineEntity, data['outlineEntityId']) if data.get('outlineEntityId', False) else False
        self.generation_type = self._get_outline_generation_type()


    def handle(self):
        pages_to_generate = self._get_all_pages_to_generate()
        generated_page_ids = self._get_page_ids_already_generated()

        pages_to_generate_ids = [page.id for page in pages_to_generate]
        all_pages_generated = collections.Counter(generated_page_ids) == collections.Counter(pages_to_generate_ids)

        if all_pages_generated:
            return GenerateOutlinePagesJobFinished(self.data)

        next_page_to_generate = None
        for page in pages_to_generate:
            if page.id not in generated_page_ids:
                next_page_to_generate = page
                break

        total_pages_to_generate = len(pages_to_generate)

        return GenerateLessonPageProcessStarted(data={
            **self.data,
            'pageId': next_page_to_generate.id,
            'completedJobItems': len(generated_page_ids),
            'totalJobItems': total_pages_to_generate,
        })


    def _get_outline_generation_type(self):
        if self.outline_entity:
            return 'OUTLINE_ENTITY'

        return 'FULL_OUTLINE'


    def _get_all_pages_to_generate(self):
        pages_to_generate = []

        match self.generation_type:
            case 'FULL_OUTLINE':
                pages_to_generate = self._get_outline_pages()
            case 'OUTLINE_ENTITY':
                pages_to_generate = self._get_entity_pages()

        return pages_to_generate


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


    def _get_page_ids_already_generated(self):
        page_ids = []
        events = self.db.query(EventStore).filter(
            EventStore.job_id == self.job.id,
            EventStore.name == 'LessonPageProcessedAndSummarizedSuccessfully'
        ).all()

        for event in events:
            page_id = event.get_data().get('pageId', None)
            if page_id and page_id not in page_ids:
                page_ids.append(page_id)

        return page_ids

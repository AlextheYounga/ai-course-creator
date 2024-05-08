import collections
from db.db import DB, OutlineEntity, Chapter, Page, EventStore
from src.events.events import GeneratePracticeChallengePageProcessStarted, GenerateFinalSkillChallengePageProcessStarted, GenerateLessonPageProcessStarted, GenerateOutlineMaterialJobFinished, GenerateMaterialFromOutlineEntityJobFinished


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
        self.outline_entity = self.db.get(OutlineEntity, data['outlineEntityId']) if data.get('outlineEntityId', False) else False
        self.page_type = data.get('pageType', False)   # lesson, challenge, final-skill-challenge


    def handle(self):
        pages_to_generate = self._get_all_pages_to_generate()
        generated_page_ids = self._get_page_ids_already_generated()

        pages_to_generate_ids = [page.id for page in pages_to_generate]
        all_pages_generated = collections.Counter(generated_page_ids) == collections.Counter(pages_to_generate_ids)

        if all_pages_generated:
            if self.outline_entity:
                return GenerateMaterialFromOutlineEntityJobFinished(self.data)
            else:
                return GenerateOutlineMaterialJobFinished(self.data)

        page_trigger_events = {
            'lesson': GenerateLessonPageProcessStarted,
            'challenge': GeneratePracticeChallengePageProcessStarted,
            'final-skill-challenge': GenerateFinalSkillChallengePageProcessStarted,
        }

        next_page_to_generate = None
        for page in pages_to_generate:
            if page.id not in generated_page_ids:
                next_page_to_generate = page
                break

        total_pages_to_generate = len(pages_to_generate)
        trigger_event = page_trigger_events[next_page_to_generate.type]

        return trigger_event(data={
            **self.data,
            'pageId': next_page_to_generate.id,
            'totalSteps': total_pages_to_generate,
        })


    def _get_all_pages_to_generate(self):
        pages_to_generate = []
        if self.outline_entity:
            pages_to_generate = self._get_entity_pages()
        else:
            pages_to_generate = self._get_outline_pages()

        if self.page_type:
            pages_to_generate = [page for page in pages_to_generate if page.type == self.page_type]

        return pages_to_generate


    def _get_outline_pages(self) -> list[Page]:
        return self.db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
        ).all()


    def _get_entity_pages(self) -> list[Page]:
        if self.outline_entity.entity_type == 'Page':
            return self.db.query(Page).filter(Page.id == self.outline_entity.entity_id).all()

        query = self.db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
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
            EventStore.job_id == self.data['jobId'],
            EventStore.name.in_([
                'LessonPageProcessedAndSummarizedSuccessfully',
                'PracticeChallengePageResponseProcessedSuccessfully',
                'FinalChallengePageResponseProcessedSuccessfully'
            ])
        ).all()

        for event in events:
            page_id = event.get_data().get('pageId', None)
            if page_id and page_id not in page_ids:
                page_ids.append(page_id)

        return page_ids

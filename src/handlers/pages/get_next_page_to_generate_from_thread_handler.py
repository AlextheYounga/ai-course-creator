import collections
from db.db import DB, Outline, OutlineEntity, Chapter, Page, Event as EventStore
from src.events.event_manager import EVENT_MANAGER
from src.events.events import GeneratePracticeChallengePageProcessStarted, GenerateFinalSkillChallengePageProcessStarted, GenerateLessonPageProcessStarted, GenerateOutlineMaterialCompletedSuccessfully
from src.handlers.pages import *


class GetNextPageToGenerateFromThreadHandler:
    """
    This handler is doing a lot! (which is not good practice)

    It is responsible for handling fetching the next page from both 
    full outline generation and outline entity generation. It checks if all pages all pages have 
    been generated and if not, triggering the next page generation event.

    If an outline entity id is present, it will fetch the pages associated with that entity.
    """

    def __init__(self, data: dict):
        self.data = data
        self.outline_entity = DB.get(OutlineEntity, data['outlineEntityId']) if data.get('outlineEntityId', False) else False
        self.page_type = data.get('pageType', False)   # lesson, challenge, final-skill-challenge


    def handle(self):
        pages_to_generate = self._get_all_pages_to_generate()
        generated_page_ids = self._get_page_ids_already_generated()

        pages_to_generate_ids = [page.id for page in pages_to_generate]
        all_pages_generated = collections.Counter(generated_page_ids) == collections.Counter(pages_to_generate_ids)

        if all_pages_generated:
            return EVENT_MANAGER.trigger(
                GenerateOutlineMaterialCompletedSuccessfully(self.data))

        page_handler = {
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
        handler = page_handler[next_page_to_generate.type]

        return EVENT_MANAGER.trigger(
            handler({
                **self.data,
                'pageId': next_page_to_generate.id,
                'totalSteps': total_pages_to_generate,
            })
        )

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
        return DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
            Page.active == True,
        ).all()


    def _get_entity_pages(self) -> list[Page]:
        if self.outline_entity.entity_type == 'Page':
            return DB.query(Page).filter(Page.id == self.outline_entity.entity_id).all()

        query = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
            Page.active == True,
        )

        if self.outline_entity.entity_type == 'Course':
            query = query.filter(
                Page.course_id == self.outline_entity.entity_id,
            )

        if self.outline_entity.entity_type == 'Chapter':
            chapter_record = DB.get(Chapter, self.outline_entity.entity_id)

            query = query.filter(
                Page.course_id == chapter_record.course_id,
                Page.chapter_id == chapter_record.id,
            )

        return query.all()


    def _get_page_ids_already_generated(self):
        page_ids = []

        events = DB.query(EventStore).filter(
            EventStore.thread_id == self.data['threadId'],
            EventStore.name.in_([
                'LessonPageProcessedAndSummarizedSuccessfully',
                'ChallengePageResponseProcessedSuccessfully',
                'FinalChallengePageResponseProcessedSuccessfully'
            ])
        ).all()

        for event in events:
            page_id = event.get_data().get('pageId', None)
            if page_id and page_id not in page_ids:
                page_ids.append(page_id)

        return page_ids

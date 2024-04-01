import collections
from db.db import DB, Thread, Outline, OutlineEntity, Page, Event as EventStore
from src.events.event_manager import EVENT_MANAGER
from src.events.events import GeneratePracticeChallengePageProcessStarted, GenerateFinalSkillChallengePageProcessStarted, GenerateLessonPageProcessStarted, GenerateOutlineMaterialCompletedSuccessfully
from src.handlers.pages import *


class GetNextPageToGenerateFromOutlineHandler:
    def __init__(self, data: dict):
        self.thread = DB.get(Thread, data['threadId'])
        self.outline = DB.get(Outline, data['outlineId'])
        self.page_type = data.get('pageType', False)   # lesson, challenge, final-skill-challenge
        self.topic = self.outline.topic


    def handle(self):
        pages_to_generate = self._get_outline_pages()
        generated_pages = self._get_pages_already_generated()

        if self.page_type:
            pages_to_generate = [page for page in pages_to_generate if page.type == self.page_type]

        pages_to_generate_ids = [page.id for page in pages_to_generate]
        all_pages_generated = collections.Counter(generated_pages) == collections.Counter(pages_to_generate_ids)

        if all_pages_generated:
            return EVENT_MANAGER.trigger(
                GenerateOutlineMaterialCompletedSuccessfully({
                    'threadId': self.thread.id,
                    'outlineId': self.outline.id,
                    'topicId': self.topic.id,
                }))

        page_handler = {
            'lesson': GenerateLessonPageProcessStarted,
            'challenge': GeneratePracticeChallengePageProcessStarted,
            'final-skill-challenge': GenerateFinalSkillChallengePageProcessStarted,
        }

        next_page_to_generate = None
        for page in pages_to_generate:
            if page.id not in generated_pages:
                next_page_to_generate = page
                break

        total_pages_to_generate = len(pages_to_generate)
        handler = page_handler[next_page_to_generate.type]

        return EVENT_MANAGER.trigger(
            handler({
                'threadId': self.thread.id,
                'outlineId': self.outline.id,
                'topicId': self.topic.id,
                'pageId': next_page_to_generate.id,
                'totalSteps': total_pages_to_generate,
            })
        )


    def _get_outline_courses(self) -> list[OutlineEntity]:
        return DB.query(OutlineEntity).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == 'Course',
        ).all()


    def _get_outline_pages(self) -> list[Page]:
        return DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == 'Page',
            Page.active == True,
        ).all()


    def _get_pages_already_generated(self):
        page_ids = []

        events = DB.query(EventStore).filter(
            EventStore.thread_id == self.thread.id,
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

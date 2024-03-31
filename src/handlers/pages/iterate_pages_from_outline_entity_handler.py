from db.db import DB, Thread, Outline, OutlineEntity, Chapter, Page
from src.events.event_manager import EVENT_MANAGER
from src.events.events import GeneratePracticeChallengePageProcessStarted, GenerateFinalSkillChallengePageProcessStarted, GenerateLessonPageProcessStarted, GenerateMaterialFromOutlineEntityCompletedSuccessfully
from src.handlers.pages import *


class IteratePagesFromOutlineEntityHandler:
    def __init__(self, data: dict):
        self.thread = DB.get(Thread, data['threadId'])
        self.outline = DB.get(Outline, data['outlineId'])
        self.outline_entity = DB.get(OutlineEntity, data['outlineEntityId'])
        self.only_page_type = data.get('onlyPageType', False)   # lesson, challenge, final-skill-challenge
        self.topic = self.outline.topic


    def handle(self):
        entity_pages = self._get_entity_pages()

        if self.only_page_type:
            entity_pages = [page for page in entity_pages if page.type == self.only_page_type]

        page_count = len(entity_pages)

        for page in entity_pages:
            if page.type == 'challenge':
                EVENT_MANAGER.trigger(GeneratePracticeChallengePageProcessStarted(self._event_payload(page, page_count)))
            elif page.type == 'final-skill-challenge':
                EVENT_MANAGER.trigger(GenerateFinalSkillChallengePageProcessStarted(self._event_payload(page, page_count)))
            else:
                EVENT_MANAGER.trigger(GenerateLessonPageProcessStarted(self._event_payload(page, page_count)))


        return EVENT_MANAGER.trigger(
            GenerateMaterialFromOutlineEntityCompletedSuccessfully({
                'threadId': self.thread.id,
                'outlineId': self.outline.id,
                'topicId': self.topic.id,
            }))


    def _get_entity_pages(self) -> list[Page]:
        if self.outline_entity.entity_type == 'Page':
            return DB.query(Page).filter(Page.id == self.outline_entity.entity_id).all()

        query = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
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


    def _event_payload(self, page: Page, page_count: int):
        return {
            'threadId': self.thread.id,
            'outlineId': self.outline.id,
            'topicId': self.topic.id,
            'pageId': page.id,
            'totalSteps': page_count,
        }

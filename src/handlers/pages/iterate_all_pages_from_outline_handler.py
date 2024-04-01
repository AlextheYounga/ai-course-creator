from db.db import DB, Outline, OutlineEntity, Page
from src.events.event_manager import EVENT_MANAGER
from src.events.events import GeneratePracticeChallengePageProcessStarted, GenerateFinalSkillChallengePageProcessStarted, GenerateLessonPageProcessStarted, GenerateOutlineMaterialCompletedSuccessfully
from src.handlers.pages import *

import progressbar


class IterateAllPagesFromOutlineHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.only_page_type = data.get('onlyPageType', False)   # lesson, challenge, final-skill-challenge
        self.topic = self.outline.topic


    def handle(self):
        outline_pages = self._get_outline_pages()

        if self.only_page_type:
            outline_pages = [page for page in outline_pages if page.type == self.only_page_type]

        page_count = len(outline_pages)

        for page in outline_pages:
            if page.type == 'challenge':
                EVENT_MANAGER.trigger(GeneratePracticeChallengePageProcessStarted(self._event_payload(page, page_count)))
            elif page.type == 'final-skill-challenge':
                EVENT_MANAGER.trigger(GenerateFinalSkillChallengePageProcessStarted(self._event_payload(page, page_count)))
            else:
                EVENT_MANAGER.trigger(GenerateLessonPageProcessStarted(self._event_payload(page, page_count)))


        return EVENT_MANAGER.trigger(
            GenerateOutlineMaterialCompletedSuccessfully({
                'threadId': self.thread_id,
                'outlineId': self.outline.id,
                'topicId': self.topic.id,
            }))


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


    def _event_payload(self, page: Page, page_count: int):
        return {
            'threadId': self.thread_id,
            'outlineId': self.outline.id,
            'topicId': self.topic.id,
            'pageId': page.id,
            'totalSteps': page_count,
        }

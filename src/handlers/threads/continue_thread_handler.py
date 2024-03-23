from db.db import DB, Outline, OutlineEntity, Page
from src.events.event_manager import EVENT_MANAGER
from src.events.events import GeneratePracticeChallengePageProcessStarted, GenerateFinalSkillChallengePageProcessStarted, GenerateLessonPageProcessStarted, GenerateOutlineMaterialCompletedSuccessfully
from src.handlers.pages import *

import progressbar


class ContinueThreadHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.only_page_type = data.get('onlyPageType', False)   # lesson, challenge, final-skill-challenge
        self.topic = self.outline.topic


    def handle(self):
        outline_pages = self._get_outline_pages()

        if self.only_page_type:
            outline_pages = [page for page in outline_pages if page.type == self.only_page_type]

        with progressbar.ProgressBar(max_value=len(outline_pages), prefix='Generating pages: ', redirect_stdout=True).start() as bar:
            for page in outline_pages:
                if page.type == 'challenge':
                    EVENT_MANAGER.trigger(GeneratePracticeChallengePageProcessStarted(self._event_payload(page)))
                elif page.type == 'final-skill-challenge':
                    EVENT_MANAGER.trigger(GenerateFinalSkillChallengePageProcessStarted(self._event_payload(page)))
                else:
                    EVENT_MANAGER.trigger(GenerateLessonPageProcessStarted(self._event_payload(page)))

                bar.increment()


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


    def _event_payload(self, page: Page):
        return {
            'threadId': self.thread_id,
            'outlineId': self.outline.id,
            'topicId': self.topic.id,
            'pageId': page.id,
        }

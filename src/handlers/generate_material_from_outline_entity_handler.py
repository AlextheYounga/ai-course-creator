from db.db import DB, Outline, OutlineEntity, Course, Chapter, Page
from src.events.event_manager import EVENT_MANAGER
from src.events.events import *
from src.handlers.pages import *

import progressbar


class GenerateMaterialFromOutlineEntityHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.outline_entity = DB.get(OutlineEntity, data['outlineEntityId'])
        self.only_page_type = data.get('onlyPageType', False)   # lesson, challenge, final-skill-challenge
        self.topic = self.outline.topic
        self.pages = self._get_entity_pages()


    def handle(self):
        if self.only_page_type:
            if self.only_page_type == 'lesson':
                return self._handle_generate_lesson_pages()
            if self.only_page_type == 'challenge':
                return self._handle_generate_practice_challenge_pages()
            if self.only_page_type == 'final-skill-challenge':
                return self._handler_generate_fsc_pages()

        self._handle_generate_lesson_pages()
        self._handle_generate_practice_challenge_pages()
        self._handler_generate_fsc_pages()


    def _handle_generate_lesson_pages(self):
        lesson_pages = [page for page in self.pages if page.type == 'lesson']
        page_count = len(lesson_pages)
        if page_count == 0: return None

        with progressbar.ProgressBar(max_value=len(lesson_pages), prefix='Generating lesson pages: ', redirect_stdout=True).start() as bar:
            for page in lesson_pages:
                EVENT_MANAGER.trigger(GenerateLessonPageProcessStarted(self._event_payload(page)))
                bar.increment()


    def _handle_generate_practice_challenge_pages(self):
        challenge_pages = [page for page in self.pages if page.type == 'challenge']
        page_count = len(challenge_pages)
        if page_count == 0: return None

        with progressbar.ProgressBar(max_value=len(challenge_pages), prefix='Generating practice challenges: ', redirect_stdout=True).start() as bar:
            for page in challenge_pages:
                EVENT_MANAGER.trigger(GeneratePracticeChallengePageProcessStarted(self._event_payload(page)))
                bar.increment()


    def _handler_generate_fsc_pages(self):
        fsc_pages = [page for page in self.pages if page.type == 'final-skill-challenge']
        page_count = len(fsc_pages)
        if page_count == 0: return None

        with progressbar.ProgressBar(max_value=len(fsc_pages), prefix='Generating final challenge pages: ', redirect_stdout=True).start() as bar:
            for page in fsc_pages:
                EVENT_MANAGER.trigger(GenerateFinalSkillChallengePageProcessStarted(self._event_payload(page)))
                bar.increment()


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


    def _event_payload(self, page: Page):
        return {
            'threadId': self.thread_id,
            'outlineId': self.outline.id,
            'topicId': self.topic.id,
            'pageId': page.id,
        }

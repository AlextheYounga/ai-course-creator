from db.db import DB, Outline, OutlineEntity, Course, Chapter, Page
from src.events.event_manager import EVENT_MANAGER
from src.events.events import *
from src.handlers.pages import *

import progressbar


class GenerateMaterialFromOutlineHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.outline_entity = DB.get(OutlineEntity, data['outlineEntityId'])
        self.only_page_type = data.get('onlyPageType', False)   # lesson, challenge, final-skill-challenge
        self.topic = self.outline.topic


    def handle(self):
        outline_courses = self._get_outline_courses()
        for course_entity in outline_courses:
            course_pages = self._get_course_pages(course_entity.entity_id)

            if self.only_page_type:
                if self.only_page_type == 'lesson':
                    self._handle_generate_lesson_pages(course_pages)
                    continue
                if self.only_page_type == 'challenge':
                    self._handle_generate_practice_challenge_pages(course_pages)
                    continue
                if self.only_page_type == 'final-skill-challenge':
                    self._handler_generate_fsc_pages(course_pages)
                    continue

            self._handle_generate_lesson_pages(course_pages)
            self._handle_generate_practice_challenge_pages(course_pages)
            self._handler_generate_fsc_pages(course_pages)


    def _handle_generate_lesson_pages(self, pages: list[Page]):
        lesson_pages = [page for page in pages if page.type == 'lesson']
        page_count = len(lesson_pages)
        if page_count == 0: return None

        with progressbar.ProgressBar(max_value=len(lesson_pages), prefix='Generating lesson pages: ', redirect_stdout=True).start() as bar:
            for page in lesson_pages:
                EVENT_MANAGER.trigger(GenerateLessonPageProcessStarted(self._event_payload(page)))
                bar.increment()


    def _handle_generate_practice_challenge_pages(self, pages: list[Page]):
        challenge_pages = [page for page in pages if page.type == 'challenge']
        page_count = len(challenge_pages)
        if page_count == 0: return None

        with progressbar.ProgressBar(max_value=len(challenge_pages), prefix='Generating practice challenges: ', redirect_stdout=True).start() as bar:
            for page in challenge_pages:
                EVENT_MANAGER.trigger(GeneratePracticeChallengePageProcessStarted(self._event_payload(page)))
                bar.increment()


    def _handler_generate_fsc_pages(self, pages: list[Page]):
        fsc_pages = [page for page in pages if page.type == 'final-skill-challenge']
        page_count = len(fsc_pages)
        if page_count == 0: return None

        with progressbar.ProgressBar(max_value=len(fsc_pages), prefix='Generating final challenge pages: ', redirect_stdout=True).start() as bar:
            for page in fsc_pages:
                EVENT_MANAGER.trigger(GenerateFinalSkillChallengePageProcessStarted(self._event_payload(page)))
                bar.increment()


    def _get_outline_courses(self) -> list[OutlineEntity]:
        return DB.query(OutlineEntity).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == 'Course',
        ).all()


    def _get_course_pages(self, course_id: int) -> list[Page]:
        return DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == 'Page',
            Page.course_id == course_id,
            Page.active == True,
        ).all()


    def _event_payload(self, page: Page):
        return {
            'threadId': self.thread_id,
            'outlineId': self.outline.id,
            'topicId': self.topic.id,
            'pageId': page.id,
        }

from db.db import DB, Outline, Page
from src.events.event_manager import EVENT_MANAGER
from src.events.events import NoExistingPageContentForLesson, NoExistingPageContentForPracticeChallenge, NoExistingPageContentForFinalChallenge
from src.events.events import NewLessonPageCreatedFromExistingPage, NewPracticeChallengePageCreatedFromExistingPage, NewFinalChallengePageCreatedFromExistingPage
from src.events.events import ExistingPageSoftDeletedForPageRegeneration


class CheckForExistingPageMaterialHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.page = DB.get(Page, data['pageId'])
        self.topic = self.outline.topic


    def handle(self) -> Page:
        if self.page.content == None:
            if self.page.type == 'lesson':
                return EVENT_MANAGER.trigger(NoExistingPageContentForLesson(self._event_payload(self.page)))
            if self.page.type == 'challenge':
                return EVENT_MANAGER.trigger(NoExistingPageContentForPracticeChallenge(self._event_payload(self.page)))
            if self.page.type == 'final-skill-challenge':
                return EVENT_MANAGER.trigger(NoExistingPageContentForFinalChallenge(self._event_payload(self.page)))
        else:
            # If here, then the page content exists and we need to handle it.
            self._soft_delete_existing_page()

            new_page = self._create_new_page_from_existing_page()

            if new_page.type == 'lesson':
                return EVENT_MANAGER.trigger(NewLessonPageCreatedFromExistingPage(self._event_payload(new_page)))
            if new_page.type == 'challenge':
                return EVENT_MANAGER.trigger(NewPracticeChallengePageCreatedFromExistingPage(self._event_payload(new_page)))
            if new_page.type == 'final-skill-challenge':
                return EVENT_MANAGER.trigger(NewFinalChallengePageCreatedFromExistingPage(self._event_payload(new_page)))


    def _create_new_page_from_existing_page(self):
        new_page = Page(
            topic_id=self.page.topic_id,
            course_id=self.page.course_id,
            chapter_id=self.page.chapter_id,
            name=self.page.name,
            slug=self.page.slug,
            path=self.page.path,
            content=None,
            summary=None,
            generated=False,
            hash=None,
            permalink=self.page.permalink,
            link='#',
            position=self.page.position,
            position_in_course=self.page.position_in_course,
            type=self.page.type,
            active=True,
        )

        if self.page.properties:
            new_page.properties = self.page.properties

        DB.add(new_page)
        DB.commit()

        return new_page


    def _soft_delete_existing_page(self):
        self.page.active = False
        DB.commit()

        EVENT_MANAGER.trigger(
            ExistingPageSoftDeletedForPageRegeneration(self._event_payload(self.page))
        )

    def _event_payload(self, page: Page):
        return {
            'threadId': self.thread_id,
            'outlineId': self.outline.id,
            'topicId': self.topic.id,
            'pageId': page.id,
        }

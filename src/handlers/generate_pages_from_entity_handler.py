from db.db import DB, Outline, OutlineEntity, Course, Page
from src.events.event_manager import EVENT_MANAGER
from src.events.events import GenerateLessonPageRequested
from openai.types.completion import Completion
import progressbar


class GeneratePagesFromEntityHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.entity_id = data['entityId']
        self.entity_type = data['entityType']
        self.topic = self.outline.topic
        self.pages = self._get_entity_pages()




    def handle(self):
        pass


    def _handle_lesson_pages(self):
        lesson_pages = [page for page in self.pages if page.type == 'lesson']
        page_count = len(lesson_pages)
        if page_count == 0: return None

        with progressbar.ProgressBar(max_value=len(lesson_pages), prefix='Generating lesson pages: ', redirect_stdout=True).start() as bar:
            for page in enumerate(lesson_pages):
                EVENT_MANAGER.trigger(
                    GenerateLessonPageRequested(self._event_payload(page))
                )


    def _get_entity_pages(self) -> list[Page]:
        if self.entity_type == 'Page':
            return DB.query(Page).filter(Page.id == self.entity_id).all()

        query = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == 'Page',
            Page.active == True,
        )

        if self.entity_type == 'Course':
            query = query.filter(Page.course_id == self.entity_id)
        if self.entity_type == 'Chapter':
            query = query.filter(Page.chapter_id == self.entity_id)

        return query.all()


    def _event_payload(self, page: Page):
        return {
            'threadId': self.thread_id,
            'outlineId': self.outline.id,
            'topicId': self.topic.id,
            'pageId': page.id,
        }

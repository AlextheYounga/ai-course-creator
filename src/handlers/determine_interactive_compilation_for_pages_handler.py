from src.events.events import LessonPageReadyForInteractiveCompilation, ChallengePageReadyForInteractiveCompilation, FinalChallengePageReadyForInteractiveCompilation
from db.db import DB, Topic, Outline, OutlineEntity, Page


class DetermineInteractiveCompilationForPagesHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.outline = self.db.get(Outline, data['outlineId'])
        self.page = self.db.get(Page, data['pageId'])
        self.topic = self.db.get(Topic, self.outline.topic_id)
        self.next_events = []

    def handle(self):
        outline_pages = self._get_outline_lesson_pages()

        chapter_pages = [p for p in outline_pages if p.chapter_id == self.page.chapter_id]
        chapter_complete = all([p.generated for p in chapter_pages])

        course_pages = [p for p in outline_pages if p.course_id == self.page.course_id]
        course_complete = all([p.generated for p in course_pages])

        self.next_events.append(LessonPageReadyForInteractiveCompilation(self.data))

        if chapter_complete:
            chapter_outline_entity = self._get_chapter_outline_entity()

            self.next_events.append(ChallengePageReadyForInteractiveCompilation({
                **self.data,
                'outlineEntityId': chapter_outline_entity.id
            }))

        if course_complete:
            course_outline_entity = self._get_course_outline_entity()

            self.next_events.append(FinalChallengePageReadyForInteractiveCompilation({
                **self.data,
                'outlineEntityId': course_outline_entity.id
            }))

        return self.next_events


    def _get_outline_lesson_pages(self):
        return self.db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == 'Page',
            Page.type == 'lesson'
        ).all()


    def _get_course_outline_entity(self):
        return self.db.query(OutlineEntity).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == 'Course',
            OutlineEntity.entity_id == self.page.course_id
        ).first()


    def _get_chapter_outline_entity(self):
        return self.db.query(OutlineEntity).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == 'Chapter',
            OutlineEntity.entity_id == self.page.chapter_id
        ).first()

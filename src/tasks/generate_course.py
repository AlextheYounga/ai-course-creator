from db.db import DB, Topic, Course, Outline, OutlineEntity, Page
from handlers.create_new_thread_handler import StartNewThreadHandler
from src.handlers.pages import *
import progressbar


class GenerateCourse:
    def __init__(self, topic_id: int, course_id: int):
        self.topic = DB.get(Topic, topic_id)
        self.course = DB.get(Course, course_id)
        self.outline = Outline.get_master_outline(DB, self.topic)
        self.thread = None
        self.pages = []


    def run(self):
        self.thread = StartNewThreadHandler(self.__class__.__name__).handle()

        self.pages = self._get_course_pages()

    def _generate_lesson_pages(self):
        generated_pages = []
        pages = [page for page in self.pages if page.type == 'lesson']

        with progressbar.ProgressBar(max_value=len(pages), prefix='Generating lesson pages: ', redirect_stdout=True).start() as bar:
            for page in pages:
                prompt = CreateLessonPagePromptHandler(self.thread.id, self.outline.id, page.id).handle()
                response = SendGenerateLessonPagePromptToLLMHandler(self.thread.id, self.outline.id, page.id).handle()


    def _get_course_pages(self):
        return DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == 'Page',
            Page.course_id == self.course.id,
            Page.active == True,
        ).all()

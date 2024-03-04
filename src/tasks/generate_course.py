from db.db import DB, Topic, Course, Outline, OutlineEntity, Page
from src.handlers.create_new_thread_handler import CreateNewThreadHandler
from src.handlers.pages import *
import progressbar


class GenerateCourse:
    def __init__(self, topic_id: int, course_id: int):
        self.topic = DB.get(Topic, topic_id)
        self.course = DB.get(Course, course_id)
        self.outline = Outline.get_master_outline(DB, self.topic)


    def run(self):
        thread = CreateNewThreadHandler({'eventName': self.__class__.__name__}).handle()
        pages = self._get_course_pages()

        # Instantiate Outline
        EVENT_MANAGER.subscribe(
            [GenerateCourseRequested],
            InstantiateOutlineHandler
        )

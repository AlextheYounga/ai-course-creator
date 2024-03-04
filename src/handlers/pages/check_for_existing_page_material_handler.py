from db.db import DB, Outline, Page
from termcolor import colored
from ...utils.log_handler import LOG_HANDLER


class CheckForExistingPageMaterialHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.page = DB.get(Page, data['pageId'])
        self.topic = self.outline.topic
        self.logging = LOG_HANDLER(self.__class__.__name__)


    def handle(self) -> Page:
        if self.page.content == None: return self.page

        # If here, then the page content exists and we need to handle it.
        self._soft_delete_existing_page()

        new_page = self._create_new_page_from_existing_page()

        return new_page


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
            nodes=None,
            generated=False,
            hash=None,
            permalink=self.page.permalink,
            link='#',
            position=self.page.position,
            position_in_course=self.page.position_in_course,
            type=self.page.type,
            active=True,
            properties=self.page.properties,
        )

        DB.add(new_page)
        DB.commit()

        return new_page


    def _soft_delete_existing_page(self):
        message = f"Thread: {self.thread_id} - Outline: {self.outline.id} - Page: {self.page.id} - Message: Soft deleting existing page."
        self.logging.info(message)
        print(colored(message, "yellow"))

        self.page.active = False
        DB.add(self.page)
        DB.commit()

from db.db import DB, Outline, OutlineEntity, Course, Page
from src.events.event_manager import EVENT_MANAGER
from src.events.events import GeneratePageMaterialRequested
from ...llm.get_llm_client import get_llm_client
from .create_lesson_page_prompt_handler import CreateLessonPagePromptHandler
from openai.types.completion import Completion
import progressbar


class GenerateCoursePagesHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.topic = self.outline.topic
        self.course = DB.get(Course, data['courseId'])




    def handle(self):
        pages = self._get_course_pages()


        with progressbar.ProgressBar(max_value=len(self.pages), prefix='Generating outline chunk: ', redirect_stdout=True).start() as bar:
            for i, page in enumerate(self.pages):

                # Build prompt
                prompt_handler = CreateLessonPagePromptHandler(self.thread_id, self.outline, page)
                prompt = prompt_handler.handle()
                messages = prompt.payload

                # Send to ChatGPT
                llm_client = get_llm_client()
                completion = llm_client.send_prompt('GenerateLesson', messages)

                response = self._save_response_payload_to_db(prompt, completion)

                EVENT_MANAGER.trigger(LessonPageResponseReceivedFromLLM({
                    'threadId': self.thread_id,
                    'outlineId': self.outline.id,
                    'topicId': self.topic.id,
                    'promptId': prompt.id,
                    'responseId': response.id,
                }))

                response_ids.append(response.id)
                prompt_ids.append(prompt.id)
                bar.update(i)


        return EVENT_MANAGER.trigger(AllLessonPagesProcessedSuccessfully({
            'threadId': self.thread_id,
            'outlineId': self.outline.id,
            'topicId': self.topic.id,
            'promptIds': prompt_ids,
            'pageIds': [page.id for page in self.pages],
            'responseIds': response_ids,
        }))



    def _handle_lesson_pages(self, pages: list[Page]):
        lesson_pages = [page for page in pages if page.page_type == 'lesson']

        with progressbar.ProgressBar(max_value=len(lesson_pages), prefix='Generating lesson pages: ', redirect_stdout=True).start() as bar:
            for i, page in enumerate(lesson_pages):

                # Build prompt
                prompt_handler = CreateLessonPagePromptHandler(self.thread_id, self.outline, page)
                prompt = prompt_handler.handle()
                messages = prompt.payload

                # Send to ChatGPT
                llm_client = get_llm_client()
                completion = llm_client.send_prompt('GenerateLesson', messages)

                response = self._save_response_payload_to_db(prompt, completion)

                EVENT_MANAGER.trigger(LessonPageResponseReceivedFromLLM({
                    'threadId': self.thread_id,
                    'outlineId': self.outline.id,
                    'topicId': self.topic.id,
                    'promptId': prompt.id,
                    'responseId': response.id,
                }))

                response_ids.append(response.id)
                prompt_ids.append(prompt.id)
                bar.update(i)


    def _get_course_pages(self):
        return DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == 'Page',
            Page.course_id == self.course.id,
            Page.active == True,
        ).all()

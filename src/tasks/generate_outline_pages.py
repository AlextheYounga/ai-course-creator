from db.db import DB, Topic, Outline
from sqlalchemy.orm.attributes import flag_modified
from src.events.event_manager import EVENT_MANAGER
from src.events.events import *
from src.handlers.pages import *
from src.handlers.create_new_thread_handler import CreateNewThreadHandler
from src.handlers.complete_thread_handler import CompleteThreadHandler
from src.handlers.generate_material_from_outline_handler import GenerateMaterialFromOutlineHandler


"""
Generates all pages from an outline. Can specify a single page type to generate.

EVENT_MANAGER.subscribe([Event], Handler)
EVENT_MANAGER.trigger(Event(data))
"""


class GenerateOutlinePages:
    def __init__(self, topic_id: int, only_page_type: str | None = None):
        EVENT_MANAGER.refresh()

        self.topic = DB.get(Topic, topic_id)
        self.only_page_type = only_page_type
        self.outline = Outline.get_master_outline(DB, self.topic)
        self.thread = CreateNewThreadHandler({'eventName': self.__class__.__name__}).handle()

    def run(self):
        EVENT_MANAGER.subscribe(
            events=[GenerateOutlineMaterialRequested],
            handler=GenerateMaterialFromOutlineHandler
        )

        EVENT_MANAGER.subscribe(
            events=[
                GenerateLessonPageProcessStarted,
                GeneratePracticeChallengePageProcessStarted,
                GenerateFinalSkillChallengePageProcessStarted
            ],
            handler=CheckForExistingPageMaterialHandler
        )

        EVENT_MANAGER.subscribe(
            events=[
                NoExistingPageContentForLesson,
                NewLessonPageCreatedFromExistingPage
            ],
            handler=CreateLessonPagePromptHandler
        )

        EVENT_MANAGER.subscribe(
            events=[
                NoExistingPageContentForPracticeChallenge,
                NewPracticeChallengePageCreatedFromExistingPage
            ],
            handler=CreatePracticeSkillChallengePromptHandler
        )

        EVENT_MANAGER.subscribe(
            events=[
                NoExistingPageContentForFinalChallenge,
                NewFinalChallengePageCreatedFromExistingPage
            ],
            handler=CreateFinalSkillChallengePromptHandler
        )

        EVENT_MANAGER.subscribe(
            events=[LessonPagePromptCreated],
            handler=SendGenerateLessonPagePromptToLLMHandler
        )

        EVENT_MANAGER.subscribe(
            events=[PracticeChallengePagePromptCreated],
            handler=SendGeneratePracticeChallengePromptToLLMHandler
        )

        EVENT_MANAGER.subscribe(
            events=[FinalSkillChallengePagePromptCreated],
            handler=SendGenerateFinalChallengePromptToLLMHandler
        )

        EVENT_MANAGER.subscribe(
            events=[LessonPageResponseReceivedFromLLM],
            handler=ProcessLessonPageResponseHandler
        )

        EVENT_MANAGER.subscribe(
            events=[LessonPageResponseProcessedSuccessfully],
            handler=GenerateLessonPageSummaryHandler
        )

        EVENT_MANAGER.subscribe(
            events=[PracticeChallengePageResponseReceivedFromLLM],
            handler=ProcessChallengePageResponseHandler
        )

        EVENT_MANAGER.subscribe(
            events=[FinalSkillChallengePageResponseReceivedFromLLM],
            handler=ProcessChallengePageResponseHandler
        )

        EVENT_MANAGER.subscribe(
            events=[GenerateOutlineMaterialCompletedSuccessfully],
            handler=CompleteThreadHandler
        )

        self.__save_event_handlers_to_thread()

        # Trigger starting event
        EVENT_MANAGER.trigger(
            GenerateOutlineMaterialRequested({
                'threadId': self.thread.id,
                'topicId': self.topic.id,
                'outlineId': self.outline.id,
                'onlyPageType': self.only_page_type
            })
        )

        print('Done')


    def __save_event_handlers_to_thread(self):
        self.thread.properties = {
            'eventHandlers': EVENT_MANAGER.dump_handlers()
        }
        flag_modified(self.thread, 'properties')
        DB.commit()

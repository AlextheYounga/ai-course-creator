from db.db import DB, Topic, OutlineEntity
from ..events.event_manager import EVENT_MANAGER
from ..events.events import *
from src.handlers.pages import *
from src.handlers.create_new_thread_handler import CreateNewThreadHandler
from src.handlers.generate_pages_from_entity_handler import GeneratePagesFromEntityHandler

"""
EVENT_MANAGER.subscribe([Event], Handler)
EVENT_MANAGER.trigger(Event(data))

See `docs/tasks/generate-pages-flow.md` for more information
"""


class GenerateEntityPages:
    def __init__(self, topic_id: int, outline_entity_id: int):
        self.topic = DB.get(Topic, topic_id)
        self.outline_entity = DB.get(OutlineEntity, outline_entity_id)
        self.outline = self.outline_entity.outline
        self.thread = CreateNewThreadHandler({'eventName': self.__class__.__name__}).handle()

    def run(self):
        EVENT_MANAGER.subscribe(
            events=[GeneratePagesFromEntityRequested],
            handler=GeneratePagesFromEntityHandler
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


        # Trigger starting event
        EVENT_MANAGER.trigger(
            GeneratePagesFromEntityRequested({
                'threadId': self.thread.id,
                'topicId': self.topic.id,
                'outlineEntityId': self.outline_entity.id,
                'outlineId': self.outline.id,
            })
        )

        print('Done')

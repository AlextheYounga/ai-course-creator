from db.db import DB, Topic, OutlineEntity
from ..events.event_manager import EVENT_MANAGER
from ..events.events import *
from src.handlers.pages import *
from src.handlers.create_new_thread_handler import CreateNewThreadHandler
from src.handlers.generate_pages_from_entity_handler import GeneratePagesFromEntityHandler

"""
EVENT_MANAGER.subscribe([Event], Handler)
EVENT_MANAGER.trigger(Event(data))

GeneratePagesFromEntityRequested
    GeneratePagesFromEntityHandler
        GenerateLessonPageProcessStarted
            CheckForExistingPageMaterialHandler
                CreateLessonPagePromptHandler
"""


class GeneratePages:
    def __init__(self, topic_id: int, outline_entity_id: int):
        self.topic = DB.get(Topic, topic_id)
        self.outline_entity = DB.get(OutlineEntity, outline_entity_id)
        self.outline = self.outline_entity.outline

    def run(self):
        thread = CreateNewThreadHandler({'eventName': self.__class__.__name__}).handle()

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
            events=[GeneratePracticeChallengePageProcessStarted],
            handler=CreatePracticeSkillChallengePromptHandler
        )

        EVENT_MANAGER.subscribe(
            events=[GenerateFinalSkillChallengePageProcessStarted],
            handler=CreateFinalSkillChallengePromptHandler
        )

        EVENT_MANAGER.subscribe(
            events=[],
            handler=CreateLessonPagePromptHandler
        )

        EVENT_MANAGER.subscribe(
            events=[GeneratePracticeChallengePageProcessStarted],
            handler=CreatePracticeSkillChallengePromptHandler
        )

        EVENT_MANAGER.subscribe(
            events=[GenerateFinalSkillChallengePageProcessStarted],
            handler=CreateFinalSkillChallengePromptHandler
        )

        # Trigger starting event
        EVENT_MANAGER.trigger(
            GeneratePagesFromEntityRequested({
                'threadId': thread.id,
                'topicId': self.topic.id,
                'outlineEntityId': self.outline_entity.id,
                'outlineId': self.outline.id,
            })
        )

        print('Done')

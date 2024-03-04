from db.db import DB, Topic, Outline
from ..events.event_manager import EVENT_MANAGER
from ..events.events import *
from src.handlers.pages import *
from src.handlers.create_new_thread_handler import CreateNewThreadHandler
from src.handlers.generate_pages_from_entity_handler import GeneratePagesFromEntityHandler

"""
EVENT_MANAGER.subscribe([Event], Handler)
EVENT_MANAGER.trigger(Event(data))
"""


class GeneratePages:
    def __init__(self, topic_id: int, entity_type: str, entity_id: int):
        self.topic = DB.get(Topic, topic_id)
        self.outline = Outline.get_master_outline(DB, self.topic)
        self.entity_type = entity_type
        self.entity_id = entity_id

    def run(self):
        thread = CreateNewThreadHandler({'eventName': self.__class__.__name__}).handle()

        EVENT_MANAGER.subscribe(
            events=[GeneratePagesFromEntityRequested],
            handler=GeneratePagesFromEntityHandler
        )


        EVENT_MANAGER.subscribe(
            events=[GenerateLessonPageRequested],
            handler=CreateLessonPagePromptHandler
        )

        EVENT_MANAGER.subscribe(
            events=[GenerateLessonPageRequested],
            handler=CreateLessonPagePromptHandler
        )

        # Trigger starting event
        EVENT_MANAGER.trigger(
            GeneratePagesFromEntityRequested({
                'threadId': thread.id,
                'topicId': self.topic.id,
                'outlineId': self.outline.id,
                'entityType': self.entity_type,
                'entityId': self.entity_id
            })
        )

        print('Done')

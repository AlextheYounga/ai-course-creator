from db.db import DB, Thread, Topic, Outline
from sqlalchemy.orm.attributes import flag_modified
from src.events.event_manager import EVENT_MANAGER
from ..pipes.generate_pages_pipeline import GeneratePagesEventPipeline
from ..events.events import GenerateOutlineMaterialRequested
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
        self.thread = Thread.start(self.__class__.__name__, DB)

    def run(self):
        # Create first event handler associatation
        EVENT_MANAGER.subscribe(
            events=[GenerateOutlineMaterialRequested],
            handler=GenerateMaterialFromOutlineHandler
        )

        # Main thread of events
        GeneratePagesEventPipeline.subscribe_all(EVENT_MANAGER)

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

        # Finish thread
        self.thread.set_complete(DB)


    def __save_event_handlers_to_thread(self):
        self.thread.properties = {
            'eventHandlers': EVENT_MANAGER.dump_handlers()
        }
        flag_modified(self.thread, 'properties')
        DB.commit()

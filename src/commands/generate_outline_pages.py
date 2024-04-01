from db.db import DB, Thread, Topic, Outline
from src.events.event_manager import EVENT_MANAGER
from ..pipelines.generate_pages_pipeline import GeneratePagesEventPipeline
from ..events.events import GenerateOutlineMaterialRequested
from ..handlers.pages.iterate_all_pages_from_outline_handler import IterateAllPagesFromOutlineHandler


# Generates all pages from an outline. Can specify a single page type to generate.
# EVENT_MANAGER.subscribe([Event], Handler)
# EVENT_MANAGER.trigger(Event(data))


class GenerateOutlinePages:
    def __init__(self, topic_id: int, only_page_type: str | None = None, progress_bar: bool = True):
        EVENT_MANAGER.refresh()
        EVENT_MANAGER.show_progress = progress_bar

        self.topic = DB.get(Topic, topic_id)
        self.only_page_type = only_page_type
        self.outline = Outline.get_master_outline(DB, self.topic)
        self.thread = Thread.start(DB, self.__class__.__name__)

    def run(self):
        # Create first event handler associatation
        EVENT_MANAGER.subscribe(
            events=[GenerateOutlineMaterialRequested],
            handler=IterateAllPagesFromOutlineHandler
        )

        # Main thread of events
        GeneratePagesEventPipeline.subscribe_all(EVENT_MANAGER)

        self.thread.update_properties(DB, {'eventHandlers': EVENT_MANAGER.dump_handlers()})

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

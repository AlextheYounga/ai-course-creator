from db.db import DB, Thread, Topic, OutlineEntity
from src.events.event_manager import EVENT_MANAGER
from ..pipelines.generate_pages_pipeline import GeneratePagesEventPipeline
from ..events.events import GeneratePagesFromOutlineEntityRequested
from ..handlers.pages.get_next_page_to_generate_from_thread_handler import GetNextPageToGenerateFromThreadHandler


# Generates pages from a single outline entity

# EVENT_MANAGER.subscribe([Event], Handler)
# EVENT_MANAGER.trigger(Event(data))

# See `docs/tasks/generate-outline-entity-pages-flow.md` for more information


class GeneratePagesFromOutlineEntity:
    def __init__(self, topic_id: int, outline_entity_id: int, page_type: str | None = None, progress_bar: bool = True):
        EVENT_MANAGER.refresh()
        EVENT_MANAGER.show_progress = progress_bar

        self.topic = DB.get(Topic, topic_id)
        self.outline_entity = DB.get(OutlineEntity, outline_entity_id)
        self.page_type = page_type
        self.outline = self.outline_entity.outline
        self.thread = Thread.start(DB, self.__class__.__name__)

    def run(self):
        EVENT_MANAGER.subscribe(
            events=[GeneratePagesFromOutlineEntityRequested],
            handler=GetNextPageToGenerateFromThreadHandler
        )

        # Main thread of events
        GeneratePagesEventPipeline.subscribe_all(EVENT_MANAGER)

        self.thread.update_properties(DB, {'eventHandlers': EVENT_MANAGER.dump_handlers()})

        # Trigger starting event
        EVENT_MANAGER.trigger(
            GeneratePagesFromOutlineEntityRequested({
                'threadId': self.thread.id,
                'topicId': self.topic.id,
                'outlineEntityId': self.outline_entity.id,
                'outlineId': self.outline.id,
                'pageType': self.page_type
            })
        )

        # Finish thread
        self.thread.set_complete(DB)

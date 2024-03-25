from db.db import DB, Thread, Topic, OutlineEntity
from src.events.event_manager import EVENT_MANAGER
from ..pipelines.generate_pages_pipeline import GeneratePagesEventPipeline
from ..events.events import GeneratePagesFromOutlineEntityRequested
from src.handlers.generate_material_from_outline_entity_handler import GenerateMaterialFromOutlineEntityHandler
from sqlalchemy.orm.attributes import flag_modified


"""
Generates pages from a single outline entity

EVENT_MANAGER.subscribe([Event], Handler)
EVENT_MANAGER.trigger(Event(data))

See `docs/tasks/generate-outline-entity-pages-flow.md` for more information
"""


class GeneratePagesFromOutlineEntity:
    def __init__(self, topic_id: int, outline_entity_id: int, only_page_type: str | None = None):
        EVENT_MANAGER.refresh()

        self.topic = DB.get(Topic, topic_id)
        self.outline_entity = DB.get(OutlineEntity, outline_entity_id)
        self.only_page_type = only_page_type
        self.outline = self.outline_entity.outline
        self.thread = Thread.start(self.__class__.__name__, DB)

    def run(self):
        EVENT_MANAGER.subscribe(
            events=[GeneratePagesFromOutlineEntityRequested],
            handler=GenerateMaterialFromOutlineEntityHandler
        )

        # Main thread of events
        GeneratePagesEventPipeline.subscribe_all(EVENT_MANAGER)

        self.__save_event_handlers_to_thread()

        # Trigger starting event
        EVENT_MANAGER.trigger(
            GeneratePagesFromOutlineEntityRequested({
                'threadId': self.thread.id,
                'topicId': self.topic.id,
                'outlineEntityId': self.outline_entity.id,
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

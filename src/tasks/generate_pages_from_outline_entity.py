from db.db import DB, Topic, OutlineEntity
from src.events.event_manager import EVENT_MANAGER
from ..pipes.generate_pages_pipeline import GeneratePagesEventPipeline
from ..events.events import GeneratePagesFromOutlineEntityRequested
from src.handlers.threads.create_new_thread_handler import CreateNewThreadHandler
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
        self.thread = CreateNewThreadHandler({'eventName': self.__class__.__name__}).handle()

    def run(self):
        EVENT_MANAGER.subscribe(
            events=[GeneratePagesFromOutlineEntityRequested],
            handler=GenerateMaterialFromOutlineEntityHandler
        )

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

        print('Done')


    def __save_event_handlers_to_thread(self):
        self.thread.properties = {
            'eventHandlers': EVENT_MANAGER.dump_handlers()
        }
        flag_modified(self.thread, 'properties')
        DB.commit()

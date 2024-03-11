from db.db import DB, Topic
from ..events.event_manager import EVENT_MANAGER
from ..events.events import GenerateOutlineRequested
from ..pipes.generate_outline_pipeline import GenerateOutlineEventPipeline
from src.handlers.create_new_thread_handler import CreateNewThreadHandler
from sqlalchemy.orm.attributes import flag_modified

"""
EVENT_MANAGER.subscribe([Event], Handler)
EVENT_MANAGER.trigger(Event(data))

See `docs/tasks/generate-outline-flow.md` for more information
"""


class GenerateOutline:
    def __init__(self, topic_id: int):
        EVENT_MANAGER.refresh()

        self.topic = DB.get(Topic, topic_id)
        self.thread = CreateNewThreadHandler({'eventName': self.__class__.__name__}).handle()

    def run(self):
        GenerateOutlineEventPipeline.subscribe_all(EVENT_MANAGER)

        self.__save_event_handlers_to_thread()

        # Trigger starting event
        EVENT_MANAGER.trigger(
            GenerateOutlineRequested({
                'threadId': self.thread.id,
                'topicId': self.topic.id
            })
        )

        print('Done')


    def __save_event_handlers_to_thread(self):
        self.thread.properties = {
            'eventHandlers': EVENT_MANAGER.dump_handlers()
        }
        flag_modified(self.thread, 'properties')
        DB.commit()

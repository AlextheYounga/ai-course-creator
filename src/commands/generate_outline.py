from db.db import DB, Thread, Topic
from ..events.event_manager import EVENT_MANAGER
from ..events.events import GenerateOutlineRequested
from ..pipelines.generate_outline_pipeline import GenerateOutlineEventPipeline

# EVENT_MANAGER.subscribe([Event], Handler)
# EVENT_MANAGER.trigger(Event(data))
# See `docs/tasks/generate-outline-flow.md` for more information


class GenerateOutline:
    def __init__(self, topic_id: int):
        EVENT_MANAGER.refresh()

        self.topic = DB.get(Topic, topic_id)
        self.thread = Thread.start(DB, self.__class__.__name__)

    def run(self):
        # Main thread of events
        GenerateOutlineEventPipeline.subscribe_all(EVENT_MANAGER)

        self.thread.update_properties(DB, {'eventHandlers': EVENT_MANAGER.dump_handlers()})

        # Trigger starting event
        EVENT_MANAGER.trigger(
            GenerateOutlineRequested({
                'threadId': self.thread.id,
                'topicId': self.topic.id
            })
        )

        # Finish thread
        self.thread.set_complete(DB)

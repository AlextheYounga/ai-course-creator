from db.db import DB, Thread, Event as EventStore
from ..events.event_manager import EVENT_MANAGER
from ..handlers.pages.get_next_page_to_generate_from_thread_handler import GetNextPageToGenerateFromThreadHandler
from ..pipelines.generate_outline_pipeline import GenerateOutlineEventPipeline
from ..pipelines.generate_pages_pipeline import GeneratePagesEventPipeline

# EVENT_MANAGER.subscribe([Event], Handler)
# EVENT_MANAGER.trigger(Event(data))
# See `docs/tasks/generate-outline-flow.md` for more information

PIPELINE_MAPPING = {
    'GenerateOutline': GenerateOutlineEventPipeline,
    'GeneratePagesFromOutlineEntity': GeneratePagesEventPipeline,
    'GeneratePagesFromOutline': GeneratePagesEventPipeline
}


class ResumeThread:
    def __init__(self, thread_id: int, progress_bar: bool = True):
        EVENT_MANAGER.refresh()
        EVENT_MANAGER.show_progress = progress_bar

        self.thread = DB.get(Thread, thread_id)


    def run(self):
        if self.thread.name == 'GenerateOutline':
            raise Exception('Resume GenerateOutline thread is not yet implemented. WIP')


        pipeline = PIPELINE_MAPPING.get(self.thread.name)
        if not pipeline:
            raise Exception(f'Pipeline for {self.thread.name} not found')

        pipeline.subscribe_all(EVENT_MANAGER)

        last_event = self._get_last_event()

        # Get next page to generate from thread
        EVENT_MANAGER.trigger(
            GetNextPageToGenerateFromThreadHandler(last_event.data)
        )

        # Finish thread
        self.thread.set_complete(DB)


    def _get_last_event(self):
        return DB.query(EventStore).filter(
            EventStore.thread_id == self.thread.id
        ).order_by(
            EventStore.id.desc()
        ).first()

from db.db import DB, Topic, Outline
from src.events.event_manager import EVENT_MANAGER
from src.events.events import NewOutlineInstantiated
import os



class InstantiateOutlineHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.topic = DB.get(Topic, data['topicId'])


    def handle(self) -> NewOutlineInstantiated:
        existing_outline_count = DB.query(Outline).filter(Outline.topic_id == self.topic.id).count()
        next_outline_number = str(existing_outline_count + 1)
        outline_name = f"series-{next_outline_number}"


        new_outline = Outline(
            topic_id=self.topic.id,
            name=outline_name,
            file_path=self._default_outline_file_path(),
        )

        DB.add(new_outline)
        DB.commit()

        return self.__trigger_completion_event({
            'topicId': self.topic.id,
            'outlineId': new_outline.id
        })


    def _default_outline_file_path(self):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
        output_path = f"{output_directory}/{self.topic.slug}"
        default_file_path = f"{output_path}/master-outline.yaml"

        return default_file_path


    def __trigger_completion_event(self, data: dict):
        EVENT_MANAGER.trigger(NewOutlineInstantiated(data))

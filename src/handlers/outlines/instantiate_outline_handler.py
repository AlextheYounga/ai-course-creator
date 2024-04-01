import os
from db.db import DB, Topic, Outline
from src.events.event_manager import EVENT_MANAGER
from src.events.events import NewOutlineInstantiated



class InstantiateOutlineHandler:
    def __init__(self, data: dict):
        self.data = data
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

        return EVENT_MANAGER.trigger(
            NewOutlineInstantiated({
                **self.data,
                'outlineId': new_outline.id
            }))


    def _default_outline_file_path(self):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
        output_path = f"{output_directory}/{self.topic.slug}"
        default_file_path = f"{output_path}/master-outline.yaml"

        return default_file_path

from db.db import DB, Thread
from src.events.event_manager import EVENT_MANAGER
from src.events.events import NewThreadCreated
import os


class CreateNewThreadHandler:
    def __init__(self, data: dict):
        self.event_name = data['eventName']


    def handle(self) -> NewThreadCreated:
        pid = os.getpid()

        thread = Thread(
            name=self.event_name,
            pid=pid
        )

        DB.add(thread)
        DB.commit()

        return self.__trigger_completion_event({'threadId': thread.id})

    def __trigger_completion_event(self, data: dict):
        EVENT_MANAGER.trigger(NewThreadCreated(data))

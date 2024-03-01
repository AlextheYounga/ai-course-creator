import os
from db.db import DB, Thread


class CreateNewThreadHandler:
    def __init__(self, data: dict):
        self.event_name = data['eventName']


    def handle(self) -> Thread:
        pid = os.getpid()

        thread = Thread(
            name=self.event_name,
            pid=pid
        )

        DB.add(thread)
        DB.commit()

        return thread

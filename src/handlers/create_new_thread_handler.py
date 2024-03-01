import os
from db.db import DB, Thread


class CreateNewThreadHandler:
    def __init__(self, event_name: str):
        self.event_name = event_name


    def handle(self) -> Thread:
        pid = os.getpid()

        thread = Thread(
            name=self.event_name,
            pid=pid
        )

        DB.add(thread)
        DB.commit()

        return thread

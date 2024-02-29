import os
from db.db import DB, Thread
from termcolor import colored


class StartNewThreadHandler:
    def __init__(self, thread_name: str):
        self.thread_name = thread_name


    def handle(self) -> Thread:
        print(colored(f"\nGenerating new thread {self.thread_name}...", "yellow"))

        pid = os.getpid()

        thread = Thread(
            name=self.thread_name,
            pid=pid
        )

        DB.add(thread)
        DB.commit()

        return thread

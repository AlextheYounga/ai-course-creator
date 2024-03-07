from db.db import DB, Thread


class CompleteThreadHandler:
    def __init__(self, data: dict):
        self.thread = DB.get(Thread, data['threadId'])


    def handle(self) -> Thread:
        self.thread.status = 'completed'
        DB.commit()

        return self.thread

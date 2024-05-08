import os
from db.db import DB, Topic, Outline
from src.events.events import NewOutlineInstantiated



class InstantiateOutlineHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.topic = self.db.get(Topic, data['topicId'])


    def handle(self):
        existing_outline_count = self.db.query(Outline).filter(Outline.topic_id == self.topic.id).count()
        next_outline_number = str(existing_outline_count + 1)
        outline_name = f"series-{next_outline_number}"

        new_outline = Outline(
            topic_id=self.topic.id,
            name=outline_name,
        )

        self.db.add(new_outline)
        self.db.commit()

        return NewOutlineInstantiated({**self.data, 'outlineId': new_outline.id})

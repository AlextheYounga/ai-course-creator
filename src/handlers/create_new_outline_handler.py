from termcolor import colored
import yaml
from db.db import DB, Topic, Outline
from .create_outline_entities_from_outline_handler import CreateOutlineEntitiesFromOutlineHandler
from src.events.events import NewOutlineCreated



class CreateNewOutlineHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.topic = self.db.get(Topic, data['topicId'])
        self.outline_data = self._read_outline_data(data['outlineData'])
        self.type = data.get('type', 'course')


    def handle(self):
        outline_hash = Outline.hash_outline(self.outline_data)
        outline = self.db.query(Outline).filter(Outline.hash == outline_hash).first()

        if outline:
            print(colored(f"Outline already exists with hash {outline_hash}", "red"))

        # Create new outline record
        new_outline = Outline(
            topic_id=self.topic.id,
            name=self._create_outline_name(),
            outline_data=self.outline_data,
            type=self.type,
            hash=outline_hash,
        )

        self.db.add(new_outline)
        self.db.commit()

        self.topic.master_outline_id = new_outline.id

        self.db.commit()

        # Create outline entities
        CreateOutlineEntitiesFromOutlineHandler({
            **self.data,
            'outlineId': new_outline.id,
        }).handle()

        return NewOutlineCreated({
            **self.data,
            'outlineId': new_outline.id
        })


    def _create_outline_name(self):
        existing_outline_count = self.db.query(Outline).filter(Outline.topic_id == self.topic.id).count()
        next_outline_number = str(existing_outline_count + 1)
        outline_name = f"series-{next_outline_number}"

        return outline_name


    def _read_outline_data(self, data):
        if isinstance(data, str):
            # Yaml string
            return yaml.safe_load(data)
        else:
            return data

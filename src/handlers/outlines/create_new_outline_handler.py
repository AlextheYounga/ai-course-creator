from termcolor import colored
import yaml
import os
from db.db import DB, Topic, Outline
from .create_outline_entities_from_outline_handler import CreateOutlineEntitiesFromOutlineHandler
from src.events.event_manager import EVENT_MANAGER
from src.events.events import NewOutlineCreated



class CreateNewOutlineHandler:
    def __init__(self, data: dict):
        self.data = data
        self.topic = DB.get(Topic, data['topicId'])
        self.outline_data = self._read_outline_data(data['outlineData'])


    def handle(self):
        outline_hash = Outline.hash_outline(self.outline_data)
        outline = DB.query(Outline).filter(Outline.hash == outline_hash).first()

        if outline:
            print(colored(f"Outline already exists with hash {outline_hash}", "red"))

        # Create new outline record
        new_outline = Outline(
            topic_id=self.topic.id,
            name=self._create_outline_name(),
            file_path=self._default_outline_file_path(),
            outline_data=self.outline_data,
            hash=outline_hash,
            properties={}
        )

        DB.add(new_outline)
        DB.commit()

        self.topic.master_outline_id = new_outline.id

        DB.commit()

        print(colored(f"New outline created {new_outline.name}\n", "green"))
        print(colored(f"New master outline set {new_outline.id}\n", "green"))

        # Create outline entities
        CreateOutlineEntitiesFromOutlineHandler({
            **self.data,
            'outlineId': new_outline.id,

        }).handle()

        return EVENT_MANAGER.trigger(
            NewOutlineCreated({
                **self.data,
                'outlineId': new_outline.id
            }))


    def _create_outline_name(self):
        existing_outline_count = DB.query(Outline).filter(Outline.topic_id == self.topic.id).count()
        next_outline_number = str(existing_outline_count + 1)
        outline_name = f"series-{next_outline_number}"

        return outline_name


    def _read_outline_data(self, data):
        if isinstance(data, str):
            # Yaml string
            return yaml.safe_load(data)
        else:
            return data


    def _default_outline_file_path(self):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
        output_path = f"{output_directory}/{self.topic.slug}"
        default_file_path = f"{output_path}/master-outline.yaml"

        return default_file_path

from db.db import DB, Topic, Outline
from .create_outline_entities_from_outline_handler import CreateOutlineEntitiesFromOutlineHandler
from src.events.event_manager import EVENT_MANAGER
from src.events.events import OutlineEntitiesCreatedFromOutline
import os



class InstantiateOutlineHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.topic = DB.get(Topic, data['topicId'])
        self.outline_data = data['outlineData']  # yaml data


    def handle(self):
        topic = session.get(Topic, topic_id)

        outline_data = open(outline_file).read()
        outline_hash = self.hash_outline(outline_data)
        outline = session.query(self).filter(self.hash == outline_hash).first()

        if outline:
            print(colored(f"Outline already exists with hash {outline_hash}", "red"))

        # Create new outline record
        new_outline = self.instantiate(session, topic_id)
        new_outline.master_outline = read_yaml_file(outline_file)  # Add changed outline to record
        new_outline.hash = self.hash_outline(new_outline.master_outline)
        new_outline.file_path = outline_file

        session.add(new_outline)
        session.commit()
        print(colored(f"New outline created {new_outline.name}\n", "green"))

        topic.master_outline_id = new_outline.id
        session.commit()
        print(colored(f"New master outline set {new_outline.id}\n", "green"))

        # Create outline entities
        self.create_outline_entities(session, new_outline.id)

        return new_outline

        return EVENT_MANAGER.trigger(
            NewOutlineInstantiated({
                'threadId': self.thread_id,
                'topicId': self.topic.id,
                'outlineId': new_outline.id
            }))


    def _default_outline_file_path(self):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
        output_path = f"{output_directory}/{self.topic.slug}"
        default_file_path = f"{output_path}/master-outline.yaml"

        return default_file_path

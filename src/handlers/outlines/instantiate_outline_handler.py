from db.db import DB, Topic, Thread, Outline
from ...utils.log_handler import LOG_HANDLER
import os
from termcolor import colored



class InstantiateOutlineHandler:
    def __init__(self, thread_id: int, topic_id: int):
        self.thread = DB.get(Thread, thread_id)
        self.topic = DB.get(Topic, topic_id)
        self.logging = LOG_HANDLER.getLogger(self.__class__.__name__)


    def handle(self) -> Outline:
        existing_outline_count = DB.query(Outline).filter(Outline.topic_id == self.topic.id).count()
        next_outline_number = str(existing_outline_count + 1)
        outline_name = f"series-{next_outline_number}"

        self._log_event()

        new_outline = Outline(
            topic_id=self.topic.id,
            name=outline_name,
            file_path=self._default_outline_file_path(),
        )

        return new_outline


    def _log_event(self):
        message = f"Creating new outline for topic: {self.topic.name}"
        print(colored(message, "yellow"))
        self.logging.info(message)


    def _default_outline_file_path(self):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
        output_path = f"{output_directory}/{self.topic.slug}"
        default_file_path = f"{output_path}/master-outline.yaml"

        return default_file_path

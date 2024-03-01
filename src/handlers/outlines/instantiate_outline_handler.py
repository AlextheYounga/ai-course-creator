from db.db import DB, Topic, Thread, Outline
from ...utils.log_handler import LOG_HANDLER
import os
from termcolor import colored



class InstantiateOutlineHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.topic = DB.get(Topic, data['topicId'])
        self.logging = LOG_HANDLER(self.__class__.__name__)


    def handle(self) -> Outline:
        self.__log_event()

        existing_outline_count = DB.query(Outline).filter(Outline.topic_id == self.topic.id).count()
        next_outline_number = str(existing_outline_count + 1)
        outline_name = f"series-{next_outline_number}"

        self._log_event()

        new_outline = Outline(
            topic_id=self.topic.id,
            name=outline_name,
            file_path=self._default_outline_file_path(),
        )

        DB.add(new_outline)
        DB.commit()

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

    def __log_event(self):
        self.logging.info(f"Thread: {self.thread_id}")

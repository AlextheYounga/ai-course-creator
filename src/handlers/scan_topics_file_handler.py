from db.db import DB, Topic
from src.utils.files import read_yaml_file


class ScanTopicsFileHandler:
    def __init__(self, data: dict = {}):
        self.data = data
        self.db = DB()
        self.topics_file = data.get('topicsFile', "configs/topics.yaml")

    def handle(self) -> list[Topic]:
        topics = []

        topics_file = read_yaml_file(self.topics_file)

        for name, properties in topics_file['topics'].items():
            existing_topic_record = self.db.query(Topic).filter(Topic.name == name).first()

            topic = existing_topic_record
            if existing_topic_record:
                existing_topic_record.properties = properties
            else:
                topic = self._create_topic(name, properties)

            self.db.commit()
            topics.append(topic)

        return topics


    def _create_topic(self, name: str, properties: dict):
        topic_record = Topic(
            name=name,
            slug=Topic.make_slug(name),
            properties=properties
        )

        self.db.add(topic_record)

        return topic_record

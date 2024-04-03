from db.db import DB, Topic, Outline, OutlineEntity
from src.commands.generate_pages_from_outline import GeneratePagesFromOutline
from src.commands.generate_pages_from_outline_entity import GeneratePagesFromOutlineEntity


class TaskController:
    @staticmethod
    def generate_entities(payload: dict):
        entityType = payload.get('entityType', None)
        topic = DB.get(Topic, payload['topic_id'])
        outline = DB.get(Outline, topic.master_outline_id)

        if topic and entityType:
            if entityType == 'Topic':
                task = GeneratePagesFromOutline(topic.id, entityType)
                task.run()

            else:
                entity_id = payload['id']

                outline_entity = DB.query(OutlineEntity).filter(
                    OutlineEntity.outline_id == outline.id,
                    OutlineEntity.entity_id == entity_id,
                    OutlineEntity.entity_type == entityType,
                ).first()

                task = GeneratePagesFromOutlineEntity(topic.id, outline_entity.id, None)
                task.run()

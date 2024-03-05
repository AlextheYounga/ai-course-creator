from db.db import DB, Topic, Outline, OutlineEntity, Course, Chapter, Page
from src.tasks.generate_outline_pages import GenerateOutlinePages
from src.tasks.generate_pages_from_outline_entity import GeneratePagesFromOutlineEntity


class TaskController:
    @staticmethod
    def generate_entities(payload: dict):
        entityType = payload.get('entityType', None)
        topic = DB.get(Topic, payload['topic_id'])
        outline = DB.get(Outline, topic.master_outline_id)

        if topic and entityType:
            if entityType == 'Topic':
                task = GenerateOutlinePages(topic.id, entityType)
                task.run()

            elif entityType == 'Course':
                course_id = payload['id']
                outline_entity = DB.query(OutlineEntity).filter(
                    OutlineEntity.outline_id == outline.id,
                    OutlineEntity.entity_id == course_id,
                    OutlineEntity.entity_type == "Course",
                )
                task = GeneratePagesFromOutlineEntity(topic.id, outline_entity.id, None)
                task.run()

            elif entityType == 'Chapter':
                chapter_id = payload['id']
                outline_entity = DB.query(OutlineEntity).filter(
                    OutlineEntity.outline_id == outline.id,
                    OutlineEntity.entity_id == chapter_id,
                    OutlineEntity.entity_type == "Chapter",
                )
                task = GeneratePagesFromOutlineEntity(topic.id, outline_entity.id, None)
                task.run()

            elif entityType == 'Page':
                page_id = payload['id']
                outline_entity = DB.query(OutlineEntity).filter(
                    OutlineEntity.outline_id == outline.id,
                    OutlineEntity.entity_id == page_id,
                    OutlineEntity.entity_type == "Page",
                )

                task = GeneratePagesFromOutlineEntity(topic.id, outline_entity.id, None)
                task.run()

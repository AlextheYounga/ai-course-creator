from db.db import DB, Outline

db = DB()


class OutlineEntityController:
    @staticmethod
    def get_entities(outline_id: int, entity_type: str = None):
        outline = db.get(Outline, outline_id)
        entities = Outline.get_entities(db, outline.id)

        if entity_type == 'Course':
            return entities['courses']

        if entity_type == 'Chapter':
            chapter_items = [chapter for chapter in entities['chapters'] if chapter.name != 'Final Skill Challenge']
            return chapter_items

        if entity_type == 'Page':
            return entities['pages']

        return entities

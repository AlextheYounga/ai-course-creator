from db.db import DB, Outline

db = DB()


class OutlineEntityController:
    @staticmethod
    def get_entities(outline_id: int, entity_type: str = None):
        outline = db.get(Outline, outline_id)
        entities = Outline.get_entities(db, outline.id)

        # Have to manually filter out the Final Skill Challenge
        chapter_items = [chapter for chapter in entities['chapters'] if chapter.name != 'Final Skill Challenge']

        match entity_type:
            case 'Course':
                return entities['courses']
            case 'Chapter':
                return chapter_items
            case 'Page':
                return entities['pages']
            case _:
                return {
                    'Course': entities['courses'],
                    'Chapter': chapter_items,
                    'Page': entities['pages']
                }

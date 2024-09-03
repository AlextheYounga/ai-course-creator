from db.db import DB, Topic, OutlineEntity, Page
from src.utils.parsing import parse_markdown

db = DB()


class PageController:
    @staticmethod
    def get_page(id: int):
        page_record = db.get(Page, id)
        interactive_records = page_record.interactives
        interactives = [i.apply_formats().to_dict() for i in interactive_records]
        content = parse_markdown(page_record.content)
        return {
            **page_record.to_dict(),
            'interactives': interactives,
            'content': str(content)
        }

    @staticmethod
    def get_next_page(id: int):
        page_record = db.get(Page, id)
        topic = db.get(Topic, page_record.topic_id)
        course_pages = db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == topic.master_outline_id,
            OutlineEntity.entity_type == 'Page',
            Page.course_id == page_record.course_id,
        ).order_by(
            Page.position_in_course
        ).all()
        page_ids = [p.id for p in course_pages]
        page_index = page_ids.index(id)
        return page_ids[page_index + 1] if page_index + 1 < len(page_ids) else None

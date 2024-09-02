from db.db import DB, Page
from src.utils.parsing import parse_markdown

db = DB()


class PageController:
    @staticmethod
    def get_page(id: int):
        page_record = db.get(Page, id)
        interactive_records = page_record.interactives
        interactives = [i.to_dict() for i in interactive_records]
        content = parse_markdown(page_record.content)
        return {
            **page_record.to_dict(),
            'interactives': interactives,
            'content': str(content)
        }

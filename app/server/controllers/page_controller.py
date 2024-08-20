from db.db import DB, Page
from src.utils.parsing import parse_markdown

db = DB()


class PageController:
    @staticmethod
    def get_page(id: int):
        page = db.get(Page, id)
        return page.to_dict()

    @staticmethod
    def get_page_content(id: int):
        page_record = db.get(Page, id)
        interactives = [i.to_dict() for i in page_record.interactives]
        html_content = parse_markdown(page_record.content)
        page = page_record.to_dict()
        return {
            **page,
            'interactives': interactives,
            'content': html_content
        }

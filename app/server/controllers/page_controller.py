from db.db import DB, Page

db = DB()


class PageController:
    @staticmethod
    def get_page(id: int):
        page = db.get(Page, id)

        return page.to_dict()

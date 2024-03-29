from db.db import DB, Page
import markdown
from flask import jsonify


class PageController:
    @staticmethod
    def get_page(id: int):
        page = DB.get(Page, id)

        return jsonify(page.to_dict())

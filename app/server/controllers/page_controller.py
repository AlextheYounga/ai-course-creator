from db.db import DB, Page
import markdown


class PageController:
    @staticmethod
    def get_page_html(id: int):
        page = DB.get(Page, id)

        content = page.content
        html = '<div>No Content</div>'

        if content:
            html = markdown.markdown(content, extensions=['fenced_code'])

        return html

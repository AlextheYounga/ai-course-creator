from termcolor import colored
from db.db import DB, Page
from ..handlers.mapping.map_page_content_to_nodes_handler import MapPageContentToNodesHandler


class MapPageContentToNodes:
    def run(self):
        pages = DB.query(Page).all()

        for page in pages:
            nodes = MapPageContentToNodesHandler({'pageId': page.id}).handle()

            page.update_properties(DB, {'nodes': nodes})

            print(colored(f"Page {page.id} parsed successfully", "green"))


        return pages

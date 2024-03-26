from db.db import DB, Page
from ..handlers.mapping.map_page_content_to_nodes_handler import MapPageContentToNodesHandler
from sqlalchemy.orm.attributes import flag_modified
from termcolor import colored


class MapPageContentToNodes:
    def run(self):
        pages = DB.query(Page).all()

        for page in pages:
            nodes = MapPageContentToNodesHandler({'pageId': page.id}).handle()

            updated_properties = {
                **page.get_properties(),
                "nodes": nodes,
            }

            page.properties = updated_properties

            flag_modified(page, "properties")

            DB.add(page)
            DB.commit()

            print(colored(f"Page {page.id} parsed successfully", "green"))


        return pages

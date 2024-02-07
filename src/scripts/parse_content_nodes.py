from db.db import DB, Page
from sqlalchemy import text
from src.mapping.node_parser import NodeParser


def _truncate_tables():
    tables = ['interactive', 'answer', 'question']

    for table in tables:
        DB.execute(text(f"DELETE FROM {table}"))
        DB.commit()


def parse_nodes_from_all_pages():
    _truncate_tables()

    pages = DB.query(Page).all()
    parsed_pages = []

    for page in pages:
        parsed_page = NodeParser.parse_nodes(page)

        if parsed_page:
            parsed_pages.append(parsed_page)

    return parsed_pages
